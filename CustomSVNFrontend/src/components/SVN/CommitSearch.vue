<template>

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
    <el-form-item label="Search Branches">
      <el-transfer
          v-model="form.branches"
          :data="branchesData"
          filterable
          :titles="['Available Branches', 'Selected Branches']"
          :render-content="renderBranchContent"
          @change="handleBranchChange"
      >
        <template #left-footer>
          <el-button class="transfer-footer" size="small" @click="selectAllBranches">Select All</el-button>
        </template>
        <template #right-footer>
          <el-button class="transfer-footer" size="small" @click="deselectAllBranches">Deselect All</el-button>
        </template>
      </el-transfer>
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
        <el-checkbox value="message" name="type">
          Message
        </el-checkbox>
        <el-checkbox value="author" name="type">
          Username
        </el-checkbox>
        <el-checkbox value="revision" name="type">
          Revision
        </el-checkbox>
        <el-checkbox value="file_changes" name="type">
          FileChange
        </el-checkbox>
      </el-checkbox-group>
    </el-form-item>
    <el-form-item label="Search Contents">
      <el-input v-model="form.contents" @keyup.enter="submitSearch"/>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="submitSearch" :loading="isSearching">
        {{ isSearching ? 'Searching...' : 'Search' }}
      </el-button>
      <el-button v-if="isSearching" @click="cancelSearch">Cancel</el-button>
    </el-form-item>
  </el-form>


  <!-- 顶部分页控件 -->
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
    <!-- 修改 Actions 列 -->
    <el-table-column label="Actions" width="120">
      <template #default="scope">
        <router-link :to="{ name: 'CommitDetail', params: { id: scope.row.id } }">
          <el-button type="text" size="small">View Details</el-button>
        </router-link>
      </template>
    </el-table-column>
  </el-table>
  <!-- 底部分页控件 -->
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

</template>

<script lang="ts" setup>

import {computed, onMounted, reactive, ref, watch} from 'vue';
import {debounce} from 'lodash'; // 确保安装并导入 lodash
import type {TransferProps} from 'element-plus';

import {useRepositoriesStore} from "@/store/repositories";
import {getBranches, searchCommits} from '@/services/svn_api';
import {ElMessage} from "element-plus";

import type {Branch, SearchCommitsResponse} from "@/services/interfaces";
import axios, {CancelTokenSource} from 'axios';

const searchDuration = ref<number>(0);


const store = useRepositoriesStore()
const branches = ref<Branch[]>([])
const pageSizeOptions = [100, 500, 1000, 5000, 10000]
const currentPage = ref(1)

const form = reactive({
  repository: computed({
    get: () => store.selectedRepository,
    set: (value) => {
      store.setSelectedRepository(value)
      handleChange(value)
    }
  }),
  branches: [] as string[],
  start_date: null as Date | null,
  end_date: null as Date | null,
  contents: '',
  regex_search: false,
  search_fields: ['message', 'author', 'revision', 'file_changes'],
  page_size: 100,
})


const isSearching = ref(false);
const cancelTokenSource = ref<CancelTokenSource | null>(null);

interface BranchData {
  key: string;
  label: string;
  disabled: boolean;
}

const branchesData = computed(() => {
  return branches.value.map(branch => ({
    key: branch.id,
    label: branch.name,
    disabled: branch.name === 'root'
  }));
});

const renderBranchContent: TransferProps['renderContent'] = (h, option) => {
  return h('span', {}, option.label);
};

const handleBranchChange = (value: string[], direction: 'left' | 'right', movedKeys: string[]) => {
  console.log('Branch selection changed:', value, direction, movedKeys);
  // 如果需要，可以在这里添加额外的逻辑
  debouncedSubmitSearch();
};

const selectAllBranches = () => {
  form.branches = branchesData.value.filter(branch => !branch.disabled).map(branch => branch.key);
};

const deselectAllBranches = () => {
  form.branches = [];
};

const submitSearch = async () => {
  if (isSearching.value) return;

  isSearching.value = true;
  cancelTokenSource.value = axios.CancelToken.source();
  const startTime = performance.now();

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
      ElMessage.error(results.error);
      searchResults.value = {count: 0, next: null, previous: null, results: []};
    } else {
      searchResults.value = results;
    }
  } catch (error: unknown) {
    if (axios.isCancel(error)) {
      console.log('Search canceled');
    } else {
      console.error('搜索失败:', error);
      ElMessage.error((error as Error).message || '搜索失败，请稍后重试');
    }
  } finally {
    isSearching.value = false;
    cancelTokenSource.value = null;
    const endTime = performance.now();
    searchDuration.value = Number((endTime - startTime).toFixed(2));
  }
};


// 创建一个防抖的 submitSearch 函数
const debouncedSubmitSearch = debounce(() => {
  searchDuration.value = 0;  // 重置搜索时长
  submitSearch();
}, 500);


const cancelSearch = () => {
  if (cancelTokenSource.value) {
    cancelTokenSource.value.cancel('Search canceled by user');
  }
};


// 设置默认的开始和结束时间
const setDefaultDates = () => {
  const now = new Date()
  form.start_date = new Date(now.getTime() - 24 * 60 * 60 * 1000 * 90)
  form.end_date = null
}

const loadBranches = async (repositoryId: string) => {
  try {
    branches.value = await getBranches({repo_id: repositoryId})
    setDefaultBranches()
  } catch (error) {
    console.error('获取分支列表失败:', error)
  }
}


const setDefaultBranches = () => {
  const trunkBranch = branches.value.find(branch => branch.name === '/trunk')
  form.branches = trunkBranch ? [trunkBranch.id] : []
}

// 监听表单数据的变化
watch(() => ({...form, repository: form.repository}), (newForm, oldForm) => {
  // 如果只有 contents 发生变化，不触发搜索
  if (newForm.contents !== oldForm.contents && Object.keys(newForm).every(key => key === 'contents' || newForm[key as keyof typeof newForm] === oldForm[key as keyof typeof oldForm])) {
    return;
  }

  currentPage.value = 1; // 重置页码
  debouncedSubmitSearch();
}, {deep: true});

const searchResults = ref<SearchCommitsResponse>({
  count: 0,
  next: null,
  previous: null,
  results: [],
});

onMounted(async () => {
  await store.fetchRepositories()
  setDefaultDates()
  if (store.repositories.length > 0) {
    const defaultRepositoryId = store.repositories[0].id
    store.setSelectedRepository(defaultRepositoryId)
    await loadBranches(defaultRepositoryId)
  }
})
// 修改 handleChange 函数
const handleChange = async (value: string) => {
  await loadBranches(value)
  debouncedSubmitSearch(); // 添加这行来触发搜索
}

// 修改 handleSizeChange 函数
const handleSizeChange = (val: number) => {
  form.page_size = val
  currentPage.value = 1
  debouncedSubmitSearch(); // 添加这行来触发搜索
}

// 修改 handleCurrentChange 函数
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  debouncedSubmitSearch(); // 添加这行来触发搜索
}
</script>

<style scoped>
.search-duration {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
</style>