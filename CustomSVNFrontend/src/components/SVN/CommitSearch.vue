<template>
  <el-card v-loading="loading" :element-loading-text="loadingMessage">
    <el-form :model="form" label-width="auto" style="max-width: 100%" size="small" @submit.prevent="submitSearch">
      <el-form-item label="Repository">
        <el-select
            v-model="form.repo_id"
            placeholder="please select Repository"
            @change="handleRepoChange"
        >
          <el-option
              v-for="repo in store.repositories"
              :key="repo.id"
              :label="repo.name"
              :value="repo.id"
          >
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-form-item label="Branches">
          <custom-transfer
              v-model="form.branch_ids"
              :data="branchesData"
          />
        </el-form-item>
        <el-form-item label="Authors">
          <custom-transfer
              v-model="form.authors"
              :data="authorsData"
          />
        </el-form-item>
      </el-form-item>

      <el-form-item>
        <el-form-item label="Revision Range">
          <el-col :span="11">
            <el-input-number
                v-model="form.revision_from"
                :min="1"
                placeholder="From revision"
            />
          </el-col>
          <el-col :span="2" style="text-align: center">-</el-col>
          <el-col :span="11">
            <el-input-number
                v-model="form.revision_to"
                :min="form.revision_from || 1"
                placeholder="To revision"
            />
          </el-col>
        </el-form-item>
        <el-form-item label="Time Range">
          <el-col :span="11">
            <el-date-picker
                v-model="form.date_from"
                type="date"
                placeholder="Pick a date"
                style="width: 100%"
            />
          </el-col>
          <el-col :span="2" style="text-align: center">-</el-col>
          <el-col :span="11">
            <el-date-picker
                v-model="form.date_to"
                type="date"
                placeholder="Pick a date"
                style="width: 100%"
            />
          </el-col>
        </el-form-item>
      </el-form-item>

      <el-form-item label="Regex search">
        <el-switch v-model="form.regex_search"/>
      </el-form-item>

      <el-form-item label="Search Contents">
        <el-input v-model="form.contents" placeholder="Search in message and file paths" @keyup.enter="submitSearch"/>
      </el-form-item>

      <el-form-item label="Filter Type">
        <el-select v-model="form.filter_type" placeholder="Select filter type">
          <el-option label="Message" value="message"/>
          <el-option label="File Path" value="file_path"/>
          <el-option label="Both" value="both"/>
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitSearch" :loading="loading">
          {{ loading ? 'Searching...' : 'Search' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-pagination
        v-if="searchResults.results && searchResults.results.length > 0"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="pageSizeOptions"
        :page-size="form.page_size"
        layout="total, sizes, prev, pager, next, "
        :total="searchResults.count"
    />
    <div v-if="searchDuration > 0" class="search-duration">
      Search time: {{ searchDuration }}ms
    </div>
    <el-table :data="searchResults.results" style="width: 100%">
      <el-table-column prop="revision" label="Revision" width="180"/>
      <el-table-column prop="author" label="Author" width="180"/>
      <el-table-column prop="date" label="Date" width="180">
        <template #default="scope">
          {{ $filters.formatDate(scope.row.date) }}
        </template>
      </el-table-column>
      <el-table-column prop="message" label="Message"/>
      <el-table-column label="Actions" width="120">
        <template #default="scope">
          <router-link :to="{ name: 'CommitDetail', params: { id: scope.row.id } }">
            <el-button type="text" size="small">View Details</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
        v-if="searchResults.results && searchResults.results.length > 0"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="pageSizeOptions"
        :page-size="form.page_size"
        layout="total, sizes, prev, pager, next"
        :total="searchResults.count"
    />
  </el-card>
  <el-alert v-if="error" :title="error" type="error" show-icon/>
</template>

<script lang="ts" setup>
import {computed, onMounted, reactive, ref} from 'vue';
import {useRepositoriesStore} from "@/store/repositories";
import {getCommitSearchFilterData, searchCommits} from '@/services/svn_api';
import type {BranchNameId, SearchCommitsResponse} from "@/services/interfaces";
import CustomTransfer from "@/components/Common/CustomTransfer.vue";
import {useLoadingState} from '@/composables/useLoadingState';

const searchDuration = ref<number>(0);
const store = useRepositoriesStore();
const branches = ref<BranchNameId[]>([]);
const authors = ref<string[]>([]);
const pageSizeOptions = [50, 100, 500, 1000, 5000, 10000];
const currentPage = ref(1);

const form = reactive({
  repo_id: computed({
    get: () => store.selectedRepository,
    set: (value) => {
      store.setSelectedRepository(value);
    }
  }),
  revision_from: null as number | null,
  revision_to: null as number | null,
  authors: [],
  branch_ids: [],
  date_from: null as Date | null,
  date_to: null as Date | null,
  contents: '',
  filter_type: 'both',
  regex_search: false,
  page_size: 100,
});

const {loading, error, withLoading} = useLoadingState({
  loadingMessage: 'Searching commits...',
  errorMessage: 'Failed to search commits. Please try again.'
});

const loadingMessage = 'Searching commits...';


const branchesData = computed(() => {
  return branches.value.map(branch => ({
    key: branch.id,
    label: branch.name,
  }));
});

const authorsData = computed(() => {
  return authors.value.map(author => ({
    key: author,
    label: author,
  }));
});

// 新的辅助函数，用于处理列表数据
const formatDataForBackend = (data: any): any => {
  if (Array.isArray(data)) {
    return data.join(',');
  } else if (data instanceof Date) {
    return data.toISOString().split('T')[0]; // 格式化日期为 YYYY-MM-DD
  } else if (typeof data === 'object' && data !== null) {
    return Object.fromEntries(
        Object.entries(data).map(([key, value]) => [key, formatDataForBackend(value)])
    );
  }
  return data;
};

const submitSearch = async () => {
  const startTime = performance.now();

  await withLoading(async () => {
    try {
      let searchParams: any = {
        ...form,
        date_from: form.date_from,
        date_to: form.date_to,
        revision_from: form.revision_from,
        revision_to: form.revision_to,
        page: currentPage.value,
        page_size: form.page_size,
      };

      if (form.filter_type === 'message' || form.filter_type === 'both') {
        searchParams.message_contains = form.contents;
      }

      if (form.filter_type === 'file_path' || form.filter_type === 'both') {
        searchParams.file_path_contains = form.contents;
      }

      let formattedData = formatDataForBackend(searchParams);

      const results = await searchCommits(formattedData);
      if ('error' in results) {
        throw new Error(results.error);
      } else {
        searchResults.value = results;
      }
    } catch (error: unknown) {
      console.error('Search error:', error);
      throw error;
    } finally {
      const endTime = performance.now();
      searchDuration.value = Number((endTime - startTime).toFixed(2));
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

// 新的函数，用于加载所有必要的数据
const loadAllData = async (repositoryId: string) => {
  const commit_search_filter_data = await getCommitSearchFilterData(repositoryId);
  branches.value = commit_search_filter_data.branches;
  authors.value = commit_search_filter_data.authors;
  // 如果还有其他数据需要加载，可以在这里添加
};

onMounted(async () => {
  await withLoading(async () => {
    await store.fetchRepositories();
    setDefaultDates();
    if (store.repositories.length > 0) {
      const defaultRepositoryId = store.repositories[0].id;
      store.setSelectedRepository(defaultRepositoryId);
      await loadAllData(defaultRepositoryId);
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

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  submitSearch();
};
</script>

<style scoped>
.search-duration {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
</style>