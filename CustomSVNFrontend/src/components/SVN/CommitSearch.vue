<template>
  <el-card v-loading="loading" :element-loading-text="loadingMessage">
    <el-form :model="form" label-width="auto" style="max-width: 100%" size="small" @submit.prevent="submitSearch">
      <el-form-item label="Repository">
        <el-select v-model="form.repo_id" placeholder="Please select Repository" @change="handleRepoChange">
          <el-option v-for="repo in store.repositories" :key="repo.id" :label="repo.name" :value="repo.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="Branches">
        <custom-transfer v-model="form.branch_ids" :data="branchesData" />
      </el-form-item>

      <el-form-item label="Authors">
        <custom-transfer v-model="form.authors" :data="authorsData" />
      </el-form-item>

      <el-form-item label="Revision Range">
        <el-col :span="11">
          <el-input-number v-model="form.revision_from" :min="1" placeholder="From revision" />
        </el-col>
        <el-col :span="2" style="text-align: center">-</el-col>
        <el-col :span="11">
          <el-input-number v-model="form.revision_to" :min="form.revision_from || 1" placeholder="To revision" />
        </el-col>
      </el-form-item>

      <el-form-item label="Time Range">
        <el-col :span="11">
          <el-date-picker v-model="form.date_from" type="date" placeholder="Pick a date" style="width: 100%" />
        </el-col>
        <el-col :span="2" style="text-align: center">-</el-col>
        <el-col :span="11">
          <el-date-picker v-model="form.date_to" type="date" placeholder="Pick a date" style="width: 100%" />
        </el-col>
      </el-form-item>

      <el-form-item label="Search Contents">
        <el-input v-model="form.contents" placeholder="Search in message and file paths" @keyup.enter="submitSearch" />
      </el-form-item>

      <el-form-item label="Filter Type">
        <el-select v-model="form.filter_type" placeholder="Select filter type">
          <el-option label="Message" value="message" />
          <el-option label="File Path" value="file_path" />
          <el-option label="Both" value="both" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitSearch" :loading="loading">
          {{ loading ? 'Searching...' : 'Search' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-pagination v-if="searchResults.count > 0" v-model:current-page="currentPage" v-model:page-size="form.page_size"
                   :page-sizes="pageSizeOptions" :total="searchResults.count" @size-change="handleSizeChange"
                   @current-change="handleCurrentChange" layout="total, sizes, prev, pager, next" />

    <div v-if="searchDuration > 0" class="search-duration">
      Search time: {{ searchDuration }}ms
    </div>

    <el-table :data="searchResults.results" style="width: 100%">
      <el-table-column type="expand">
        <template #default="props">
          <el-popover
              placement="right"
              :width="600"
              trigger="click"
          >
            <template #reference>
              <el-button type="text">View Details</el-button>
            </template>
            <template #default>
              <div class="commit-details">
                <h3>Commit Details</h3>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="Repository Name">{{ props.row.repository?.name }}</el-descriptions-item>
                  <el-descriptions-item label="Branch Name">{{ props.row.branch?.name }}</el-descriptions-item>
                  <el-descriptions-item label="Revision">{{ props.row.revision }}</el-descriptions-item>
                  <el-descriptions-item label="Author">{{ props.row.author }}</el-descriptions-item>
                  <el-descriptions-item label="Date">{{ $filters.formatDate(props.row.date) }}</el-descriptions-item>
                  <el-descriptions-item label="Message">{{ props.row.message }}</el-descriptions-item>
                </el-descriptions>

                <h4>File Changes</h4>
                <el-table :data="props.row.file_changes" style="width: 100%">
                  <el-table-column prop="path" label="Path" />
                  <el-table-column prop="action" label="Action" />
                  <el-table-column prop="kind" label="Kind" />
                </el-table>
              </div>
            </template>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="revision" label="Revision" width="120" />
      <el-table-column prop="author" label="Author" width="150" />
      <el-table-column prop="date" label="Date" width="180">
        <template #default="scope">
          {{ $filters.formatDate(scope.row.date) }}
        </template>
      </el-table-column>
      <el-table-column prop="message" label="Message" />
      <el-table-column label="Actions" width="120">
        <template #default="scope">
          <router-link :to="{ name: 'CommitDetail', params: { id: scope.row.id } }">
            <el-button type="text" size="small">Full Details</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-if="searchResults.results.length > 0" v-model:current-page="currentPage"
                   v-model:page-size="form.page_size" :page-sizes="pageSizeOptions" :total="searchResults.count"
                   @size-change="handleSizeChange" @current-change="handleCurrentChange" layout="total, sizes, prev, pager, next" />
  </el-card>
  <el-alert v-if="error" :title="error" type="error" show-icon />
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRepositoriesStore } from "@/store/repositories";
import { getCommitSearchFilterData, searchCommits } from '@/services/svn_api';
import type { BranchNameId, SearchCommitsResponse } from "@/services/interfaces";
import CustomTransfer from "@/components/Common/CustomTransfer.vue";
import { useLoadingState } from '@/composables/useLoadingState';
import { ElMessage } from "element-plus";

const searchDuration = ref<number>(0);
const store = useRepositoriesStore();
const branches = ref<BranchNameId[]>([]);
const authors = ref<string[]>([]);
const pageSizeOptions = [50, 100, 500, 1000, 5000, 10000];
const currentPage = ref(1);

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

const { loading, error, withLoading } = useLoadingState({
  loadingMessage: 'Searching commits...',
  errorMessage: 'Failed to search commits. Please try again.'
});

const loadingMessage = 'Searching commits...';

const branchesData = computed(() => branches.value.map(branch => ({ key: branch.id, label: branch.name })));
const authorsData = computed(() => authors.value.map(author => ({ key: author, label: author })));

const formatDataForBackend = (data: any): any => {
  if (Array.isArray(data)) return data.join(',');
  if (data instanceof Date) return data.toISOString().split('T')[0];
  if (typeof data === 'object' && data !== null) {
    return Object.fromEntries(Object.entries(data).map(([key, value]) => [key, formatDataForBackend(value)]));
  }
  return data;
};

const submitSearch = async () => {
  const startTime = performance.now();
  return await withLoading(async () => {
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
      console.error('Search error:', error);
      if (error instanceof Error) {
        ElMessage.error(error.message);
      } else {
        ElMessage.error('An unexpected error occurred');
      }
    } finally {
      searchDuration.value = Number((performance.now() - startTime).toFixed(2));
    }
  });
};

const setDefaultDates = () => {
  const now = new Date();
  form.date_from = new Date(now.getTime() - 24 * 60 * 60 * 1000 * 90);
  form.date_to = null;
};

const searchResults = ref<SearchCommitsResponse>({
  count: 0,
  next: null,
  previous: null,
  results: [],
});

const loadAllData = async (repositoryId: string) => {
  const { branches: newBranches, authors: newAuthors } = await getCommitSearchFilterData(repositoryId);
  branches.value = newBranches;
  authors.value = newAuthors;
};

onMounted(async () => {
  await withLoading(async () => {
    await store.fetchRepositories();
    setDefaultDates();
    if (store.repositories.length > 0) {
      const defaultRepositoryId = store.repositories[0].id;
      store.setSelectedRepository(defaultRepositoryId);
      await loadAllData(defaultRepositoryId);
      await submitSearch();
    }
  });
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
</script>

<style scoped>
.search-duration {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.commit-details {
  font-size: 14px;
}

.commit-details h3 {
  margin-top: 0;
  margin-bottom: 16px;
}

.commit-details h4 {
  margin-top: 16px;
  margin-bottom: 8px;
}
</style>