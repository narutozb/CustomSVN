<template>

  <el-form :model="form" label-width="auto" style="max-width: 800px" size="small">
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
      <el-checkbox-group v-model="form.branches">
        <el-checkbox
            v-for="branch in branches"
            :key="branch.id"
            :label="branch.id"
            :disabled="branch.name === 'root'"
        >
          {{ branch.name }}
        </el-checkbox>
      </el-checkbox-group>
    </el-form-item>
    <el-form-item label="StartFrom">
      <el-col :span="11">
        <el-date-picker
            v-model="form.start_date"
            type="date"
            placeholder="Pick a date"
            style="width: 100%"
        />
      </el-col>
    </el-form-item>
    <el-form-item label="EndFrom">
      <el-col :span="11">
        <el-date-picker
            v-model="form.end_date"
            type="date"
            placeholder="Pick a date"
            style="width: 100%"
        />
      </el-col>
    </el-form-item>
    <el-form-item label="Exact search">
      <el-switch v-model="form.exact_search"/>
    </el-form-item>
    <el-form-item label="Search Options">
      <el-checkbox-group v-model="form.search_type">
        <el-checkbox value="message" name="type">
          Message
        </el-checkbox>
        <el-checkbox value="auth" name="type">
          Username
        </el-checkbox>
        <el-checkbox value="revision" name="type">
          Revision
        </el-checkbox>
      </el-checkbox-group>

    </el-form-item>
    <el-form-item label="Search Contents">
      <el-input v-model="form.contents"/>
    </el-form-item>
    <el-form-item label="Page Size">
      <el-select v-model="form.page_size" placeholder="Select page size">
        <el-option
            v-for="size in pageSizeOptions"
            :key="size"
            :label="size"
            :value="size"
        />
      </el-select>
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
      layout="total, sizes, prev, pager, next, jumper"
      :total="searchResults.count"
  />

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
      layout="total, sizes, prev, pager, next, jumper"
      :total="searchResults.count"
  />
</template>

<script lang="ts" setup>

import {computed, reactive, ref, watch} from 'vue'
import {onMounted} from 'vue'
import {useRepositoriesStore} from "@/store/repositories"
import {fetchBranches, searchCommits} from '@/services/svn_api'
import {debounce} from 'lodash'
import type {Branch} from "@/services/interfaces"; // 需要安装 lodash 库


const store = useRepositoriesStore()
const branches = ref<Branch[]>([])
const pageSizeOptions = [100, 500, 1000, 5000, 10000, 20000, 50000]
const currentPage = ref(1)


// 设置默认的开始和结束时间
const setDefaultDates = () => {
  const now = new Date()
  const default_start_date = new Date(now.getTime() - 24 * 60 * 60 * 1000 * 90)
  form.start_date = default_start_date
  form.end_date = null

}

const loadBranches = async (repositoryId: string) => {
  try {
    branches.value = await fetchBranches(repositoryId) as Branch[]
    setDefaultBranches()
  } catch (error) {
    console.error('获取分支列表失败:', error)
  }
}

onMounted(async () => {
  await store.fetchRepositories()
  setDefaultDates()
  if (store.repositories.length > 0) {
    const defaultRepositoryId = store.repositories[0].id
    store.setSelectedRepository(defaultRepositoryId)
    await loadBranches(defaultRepositoryId)
  }
})

const handleChange = async (value: string) => {
  // const selectedRepo = store.repositories.find(repo => repo.id === value)
  await loadBranches(value)
}

const setDefaultBranches = () => {
  const trunkBranch = branches.value.find(branch => branch.name === '/trunk')
  form.branches = trunkBranch ? [trunkBranch.id] : []
}

const form = reactive({
  repository: computed({
    get: () => store.selectedRepository,
    set: (value) => store.setSelectedRepository(value)
  }),
  branches: [] as string[],
  start_date: null as Date | null,
  end_date: null as Date | null,
  contents: '',
  exact_search: false,
  search_type: ['message', 'auth', 'revision'],
  page_size: 100,
})

// 监听表单数据的变化
watch(form, () => {
  currentPage.value = 1 // 重置页码
  debouncedSearch()
}, {deep: true})

// 监听页码变化
watch(currentPage, () => {
  debouncedSearch()
})

const searchResults = ref({
  count: 0,
  next: null,
  previous: null,
  results: [],
})

// 使用 debounce 来避免频繁触发搜索
const debouncedSearch = debounce(async () => {
  try {
    let start_date = form.start_date ? form.start_date.toISOString().split('T')[0] : null;
    let end_date = form.end_date ? form.end_date.toISOString().split('T')[0] : null;

    const formattedData = {
      ...form,
      start_date,
      end_date,
      page: currentPage.value,
      page_size: form.page_size,
    };

    console.log('Submitting:', formattedData);
    const results = await searchCommits(formattedData);
    searchResults.value = results;
    console.log('Search results:', results);
  } catch (error) {
    console.error('搜索失败:', error);
    // 这里可以添加错误处理，比如显示一个错误消息
  }
}, 500);

const handleSizeChange = (val: number) => {
  form.page_size = val
  currentPage.value = 1
  debouncedSearch()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // 不需要在这里调用 debouncedSearch，因为 currentPage 的 watch 会处理
}


</script>