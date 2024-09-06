<template>
  <el-card v-loading="loading" :element-loading-text="loadingMessage">
    <el-form :model="form" label-width="auto" style="max-width: 100%" size="small" @submit.prevent="submitSearch">
      <el-form-item label="Repository">
        <el-select
            v-model="form.repository"
            placeholder="please select Repository"
            @change="handleChange"
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
      <el-form-item label="Branches">
        <custom-transfer
            v-model="form.branches"
            :data="branchesData"
            left-title="Available"
            right-title="Selected"
            @change="handleBranchChange"
        />
      </el-form-item>
      <el-form-item label="Time Range">
        <el-col :span="11">
          <el-date-picker
              v-model="form.start_date"
              type="date"
              placeholder="Pick a date"
              style="width: 100%"
          />
        </el-col>
        <el-col :span="2" style="text-align: center">-</el-col>
        <el-col :span="11">
          <el-date-picker
              v-model="form.end_date"
              type="date"
              placeholder="Pick a date"
              style="width: 100%"
          />
        </el-col>
      </el-form-item>
      <el-form-item label="Regex search">
        <el-switch v-model="form.regex_search"/>
      </el-form-item>
      <el-form-item label="Search Options">
        <el-checkbox-group v-model="form.search_fields">
          <el-checkbox value="message" name="type">Message</el-checkbox>
          <el-checkbox value="author" name="type">Username</el-checkbox>
          <el-checkbox value="revision" name="type">Revision</el-checkbox>
          <el-checkbox value="file_changes" name="type">FileChange</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="Search Contents">
        <el-input v-model="form.contents" @keyup.enter="submitSearch"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitSearch" :loading="loading">
          {{ loading ? 'Searching...' : 'Search' }}
        </el-button>
        <el-button v-if="loading" @click="cancelSearch">Cancel</el-button>
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
  <el-alert v-if="error" :title="error" type="error" show-icon />
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { debounce } from 'lodash';
import type { TransferProps } from 'element-plus';
import { useRepositoriesStore } from "@/store/repositories";
import { getBranches, searchCommits } from '@/services/svn_api';
import { ElMessage } from "element-plus";
import type { Branch, SearchCommitsResponse } from "@/services/interfaces";
import axios, { CancelTokenSource } from 'axios';
import CustomTransfer from "@/components/Common/CustomTransfer.vue";
import { useLoadingState } from '@/composables/useLoadingState';

const searchDuration = ref<number>(0);
const store = useRepositoriesStore();
const branches = ref<Branch[]>([]);
const pageSizeOptions = [100, 500, 1000, 5000, 10000];
const currentPage = ref(1);

const form = reactive({
  repository: computed({
    get: () => store.selectedRepository,
    set: (value) => {
      store.setSelectedRepository(value);
      handleChange(value);
    }
  }),
  branches: [] as string[],
  start_date: null as Date | null,
  end_date: null as Date | null,
  contents: '',
  regex_search: false,
  search_fields: ['message', 'author', 'revision', 'file_changes'],
  page_size: 100,
});

const { loading, error, withLoading } = useLoadingState({
  loadingMessage: 'Searching commits...',
  errorMessage: 'Failed to search commits. Please try again.'
});

const loadingMessage = 'Searching commits...';

const cancelTokenSource = ref<CancelTokenSource | null>(null);

const branchesData = computed(() => {
  const data = branches.value.map(branch => ({
    key: branch.id,
    label: branch.name,
    disabled: branch.name === 'root'
  }));
  console.log(data);
  return data;
});

const handleBranchChange = (value: string[], direction: 'left' | 'right', movedKeys: string[]) => {
  console.log('Branch selection changed:', value, direction, movedKeys);
  debouncedSubmitSearch();
};

const submitSearch = async () => {
  cancelTokenSource.value = axios.CancelToken.source();
  const startTime = performance.now();

  await withLoading(async () => {
    try {
      let start_date = form.start_date ? new Date(form.start_date.getTime() - form.start_date.getTimezoneOffset() * 60000).toISOString().split('T')[0] : null;
      let end_date = form.end_date ? new Date(form.end_date.getTime() - form.end_date.getTimezoneOffset() * 60000).toISOString().split('T')[0] : null;

      const formattedData = {
        ...form,
        start_date,
        end_date,
        page: currentPage.value,
        page_size: form.page_size,
      };

      console.log(formattedData);

      const results = await searchCommits(formattedData, cancelTokenSource.value?.token);
      if ('error' in results) {
        throw new Error(results.error);
      } else {
        searchResults.value = results;
      }
    } catch (error: unknown) {
      if (axios.isCancel(error)) {
        console.log('Search canceled');
      } else {
        throw error;
      }
    } finally {
      cancelTokenSource.value = null;
      const endTime = performance.now();
      searchDuration.value = Number((endTime - startTime).toFixed(2));
    }
  });
};

const debouncedSubmitSearch = debounce(() => {
  searchDuration.value = 0;
  submitSearch();
}, 500);

const cancelSearch = () => {
  if (cancelTokenSource.value) {
    cancelTokenSource.value.cancel('Search canceled by user');
  }
};

const setDefaultDates = () => {
  const now = new Date();
  form.start_date = new Date(now.getTime() - 24 * 60 * 60 * 1000 * 90);
  form.end_date = null;
};

const loadBranches = async (repositoryId: string) => {
  try {
    branches.value = await getBranches({repo_id: repositoryId});
  } catch (error) {
    console.error('获取分支列表失败:', error);
  }
};

watch(() => ({...form, repository: form.repository}), (newForm, oldForm) => {
  if (newForm.contents !== oldForm.contents && Object.keys(newForm).every(key => key === 'contents' || newForm[key as keyof typeof newForm] === oldForm[key as keyof typeof oldForm])) {
    return;
  }

  currentPage.value = 1;
  debouncedSubmitSearch();
}, {deep: true});

const searchResults = ref<SearchCommitsResponse>({
  count: 0,
  next: null,
  previous: null,
  results: [],
});

onMounted(async () => {
  await withLoading(async () => {
    await store.fetchRepositories();
    setDefaultDates();
    if (store.repositories.length > 0) {
      const defaultRepositoryId = store.repositories[0].id;
      store.setSelectedRepository(defaultRepositoryId);
      await loadBranches(defaultRepositoryId);
    }
  });
});

const handleChange = async (value: string) => {
  await loadBranches(value);
  debouncedSubmitSearch();
};

const handleSizeChange = (val: number) => {
  form.page_size = val;
  currentPage.value = 1;
  debouncedSubmitSearch();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  debouncedSubmitSearch();
};
</script>

<style scoped>
.search-duration {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
</style>