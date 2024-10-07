<template>
  <div class="search-container">
    <div v-if="loading" class="loading-overlay">
      <el-card class="loading-card">
        <div class="loading-content">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>Searching commits...</span>
          <el-button @click="cancelSearch" size="small">Cancel</el-button>
        </div>
      </el-card>
    </div>

    <el-card>
      <el-form :model="form" label-width="auto" style="max-width: 100%" size="small" @submit.prevent="submitSearch">
        <el-form-item label="Repository">
          <el-select v-model="form.repo_id" placeholder="Please select Repository" @change="handleRepoChange">
            <el-option v-for="repo in store.repositories" :key="repo.id" :label="repo.name" :value="repo.id"/>
          </el-select>
        </el-form-item>

        <el-form-item label="Branches">
          <custom-transfer v-model="form.branch_ids" :data="branchesData"/>
        </el-form-item>

        <el-form-item label="Authors">
          <custom-transfer v-model="form.authors" :data="authorsData"/>
        </el-form-item>

        <el-form-item label="Revision Range">
          <el-col :span="11">
            <el-input-number v-model="form.revision_from" :min="1" placeholder="From revision"/>
          </el-col>
          <el-col :span="2" style="text-align: center">-</el-col>
          <el-col :span="11">
            <el-input-number v-model="form.revision_to" :min="form.revision_from || 1" placeholder="To revision"/>
          </el-col>
        </el-form-item>

        <el-form-item label="Time Range">
          <el-col :span="11">
            <el-date-picker v-model="form.date_from" type="date" placeholder="Pick a date" style="width: 100%"/>
          </el-col>
          <el-col :span="2" style="text-align: center">-</el-col>
          <el-col :span="11">
            <el-date-picker v-model="form.date_to" type="date" placeholder="Pick a date" style="width: 100%"/>
          </el-col>
        </el-form-item>

        <el-form-item label="Search Contents">
          <el-input v-model="form.contents" placeholder="Search in message and file paths"/>
        </el-form-item>

        <el-form-item label="Filter Type">
          <el-select v-model="form.filter_type" placeholder="Select filter type">
            <el-option label="Message" value="message"/>
            <el-option label="File Path" value="file_path"/>
            <el-option label="All" value="both"/>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitSearch" :disabled="loading">
            Search
          </el-button>
        </el-form-item>
      </el-form>

      <el-pagination
          v-if="searchResults.count > 0"
          v-model:current-page="currentPage"
          v-model:page-size="form.page_size"
          :page-sizes="pageSizeOptions"
          :total="searchResults.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          layout="total, sizes, prev, pager, next"
      />

      <div v-if="searchDuration > 0" class="search-duration">
        Search time: {{ searchDuration }}ms
      </div>

      <el-table
          v-if="searchResults.results.length > 0"
          :data="searchResults.results"
          style="width: 100%"
      >
        <el-table-column label="Revision" width="120">
          <template #default="{ row }">
            <el-popover
                placement="right"
                :width="400"
                trigger="hover"
                :show-after="100"
            >
              <template #default>
                <CommitDetailPreview :commit="row" />
              </template>
              <template #reference>
                <router-link
                    :to="{ name: 'CommitDetail', params: { id: row.id } }"
                    class="revision-link"
                >
                  {{ row.revision }}
                </router-link>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column label="Author" width="150">
          <template #default="{ row }">
            <span v-html="row.author"></span>
          </template>
        </el-table-column>
        <el-table-column label="Date" width="180">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column label="Message">
          <template #default="{ row }">
            <el-tooltip :content="row.message" placement="top" :show-after="500">
              <div class="message-cell">
                <span v-html="truncateMessage(row.message)"></span>
              </div>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
          v-if="searchResults.results.length > 0"
          v-model:current-page="currentPage"
          v-model:page-size="form.page_size"
          :page-sizes="pageSizeOptions"
          :total="searchResults.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          layout="total, sizes, prev, pager, next"
      />
    </el-card>
    <el-alert v-if="error" :title="error" type="error" show-icon/>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRepositoriesStore } from "@/store/repositories";
import { getCommitSearchFilterData, searchCommits } from '@/services/svn_api';
import type { BranchNameId, SearchCommitsResponse } from "@/services/interfaces";
import CustomTransfer from "@/components/Common/CustomTransfer.vue";
import { ElMessage } from "element-plus";
import CommitDetailPreview from "@/components/SVN/CommitDetailPreview.vue";
import { Loading } from '@element-plus/icons-vue'

const store = useRepositoriesStore();
const searchDuration = ref<number>(0);
const branches = ref<BranchNameId[]>([]);
const authors = ref<string[]>([]);
const pageSizeOptions = [100, 500, 1000, 5000, 10000];
const currentPage = ref(1);
const loading = ref(false);
const error = ref<string | null>(null);
let abortController: AbortController | null = null;

const form = reactive({
  repo_id: computed({
    get: () => store.selectedRepository,
    set: (value) => store.setSelectedRepository(value)
  }),
  revision_from: null as number | null,
  revision_to: null as number | null,
  authors: [],
  branch_ids: [],
  date_from: null as Date | null,
  date_to: null as Date | null,
  contents: '',
  filter_type: 'both',
  page_size: 100,
});

const branchesData = computed(() => branches.value.map(branch => ({ key: branch.id, label: branch.name })));
const authorsData = computed(() => authors.value.map(author => ({ key: author, label: author })));

const searchResults = ref<SearchCommitsResponse>({
  count: 0,
  next: null,
  previous: null,
  results: [],
});

const formatDataForBackend = (data: any): any => {
  if (Array.isArray(data)) return data.join(',');
  if (data instanceof Date) return data.toISOString().split('T')[0];
  if (typeof data === 'object' && data !== null) {
    return Object.fromEntries(Object.entries(data).map(([key, value]) => [key, formatDataForBackend(value)]));
  }
  return data;
};

const submitSearch = async () => {
  if (loading.value) return;

  const startTime = performance.now();
  loading.value = true;
  error.value = null;
  abortController = new AbortController();

  try {
    const searchParams = {
      ...form,
      page: currentPage.value,
      message_contains: form.filter_type !== 'file_path' ? form.contents : undefined,
      file_path_contains: form.filter_type !== 'message' ? form.contents : undefined,
    };
    const formattedData = formatDataForBackend(searchParams);

    const results = await searchCommits(formattedData);

    if ('error' in results && typeof results.error === 'string') {
      throw new Error(results.error);
    } else if ('error' in results) {
      throw new Error('An unknown error occurred');
    }

    searchResults.value = results as SearchCommitsResponse;
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.log('Search was cancelled');
    } else {
      console.error('Search error:', error);
      if (error instanceof Error) {
        ElMessage.error(error.message);
      } else {
        ElMessage.error('An unexpected error occurred');
      }
    }
  } finally {
    loading.value = false;
    searchDuration.value = Number((performance.now() - startTime).toFixed(2));
    abortController = null;
  }
};

const cancelSearch = () => {
  if (abortController) {
    abortController.abort();
    loading.value = false;
    ElMessage.info('Search cancelled');
  }
};

const setDefaultDates = () => {
  const now = new Date();
  form.date_from = new Date(now.getTime() - 24 * 60 * 60 * 1000 * 90);
  form.date_to = null;
};

const loadAllData = async (repositoryId: string) => {
  const { branches: newBranches, authors: newAuthors } = await getCommitSearchFilterData(repositoryId);
  branches.value = newBranches;
  authors.value = newAuthors;
};

onMounted(async () => {
  loading.value = true;
  try {
    await store.fetchRepositories();
    setDefaultDates();
    if (store.repositories.length > 0) {
      const defaultRepositoryId = store.repositories[0].id;
      store.setSelectedRepository(defaultRepositoryId);
      await loadAllData(defaultRepositoryId);
      await submitSearch();
    }
  } catch (err) {
    console.error('Error during initialization:', err);
    error.value = 'Failed to initialize. Please try refreshing the page.';
  } finally {
    loading.value = false;
  }
});

const handleRepoChange = async (value: string) => {
  form.branch_ids = [];
  form.authors = [];
  await loadAllData(value);
};

const handleSizeChange = (val: number) => {
  form.page_size = val;
  currentPage.value = 1;
  submitSearch();
};

const handleCurrentChange = async (val: number) => {
  const previousPage = currentPage.value;
  currentPage.value = val;
  try {
    await submitSearch();
    if (searchResults.value.results.length === 0) {
      ElMessage.info("No results on this page.");
    }
  } catch (error) {
    console.error('Error changing page:', error);
    currentPage.value = previousPage;
    if (error instanceof Error && error.message.includes("No more results available")) {
      ElMessage.info("No more results available.");
    } else {
      ElMessage.error("An error occurred while changing the page. Please try again.");
    }
  }
};

const formatDate = (date: string | Date) => {
  if (!date) return 'N/A';
  const d = new Date(date);
  return d.toLocaleString();
};

const truncateMessage = (message: string, maxLength = 100) => {
  if (message.length <= maxLength) return message;
  return message.slice(0, maxLength) + '...';
};
</script>

<style scoped>
.search-container {
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 20vh;
  z-index: 9999;
}

.loading-card {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-duration {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.revision-link {
  text-decoration: none;
  color: #409EFF;
}

.revision-link:hover {
  text-decoration: underline;
}

.message-cell {
  max-width: 500px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-table .cell) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(mark) {
  background-color: yellow;
  padding: 0.2em 0;
}
</style>