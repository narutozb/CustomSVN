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
      <el-col :span="2" class="text-center">
        <span class="text-gray-500">-</span>
      </el-col>
      <el-col :span="11">
        <el-time-picker
            v-model="form.start_time"
            placeholder="Pick a time"
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
      <el-col :span="2" class="text-center">
        <span class="text-gray-500">-</span>
      </el-col>
      <el-col :span="11">
        <el-time-picker
            v-model="form.end_time"
            placeholder="Pick a time"
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
    <el-form-item>
      <el-button type="primary" @click="onSubmit">Search</el-button>
    </el-form-item>

  </el-form>


  <!-- 修改表格和分页控件 -->
  <div v-if="searchResults.results && searchResults.results.length > 0">
    <el-table :data="searchResults.results" style="width: 100%">
      <el-table-column prop="revision" label="Revision" width="180"/>
      <el-table-column prop="author" label="Author" width="180"/>
      <el-table-column prop="date" label="Date" width="180">
        <template #default="scope">
          {{ $filters.formatDate(scope.row.date) }}
        </template>
      </el-table-column>
      <el-table-column prop="message" label="Message"/>
    </el-table>

    <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="pageSizeOptions"
        :page-size="form.page_size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="searchResults.count"
    />
  </div>
</template>

<script lang="ts" setup>

import {computed, reactive, ref, watch} from 'vue'
import {onMounted} from 'vue'
import {useRepositoriesStore} from "@/store/repositories"
import {fetchBranches, searchCommits} from '@/services/svn_api'

const store = useRepositoriesStore()
const branches = ref([])
const pageSizeOptions = [100, 500, 1000, 5000, 10000, 20000, 50000]
const currentPage = ref(1)


// 设置默认的开始和结束时间
const setDefaultDates = () => {
  const now = new Date()
  // const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
  // form.start_date = yesterday
  // form.start_time = yesterday
  form.start_date = null
  form.start_time = null
  form.end_date = now
  form.end_time = null

}

const loadBranches = async (repositoryId: string) => {
  try {
    branches.value = await fetchBranches(repositoryId)
    setDefaultBranches()
  } catch (error) {
    console.error('获取分支列表失败:', error)
    // 这里可以添加错误处理，比如显示一个错误消息
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
  branches: [],
  start_date: null as Date | null,
  start_time: null as Date | null,
  end_date: null as Date | null,
  end_time: null as Date | null,
  contents: '',
  exact_search: false,
  search_type: ['message', 'auth', 'revision'],
  page_size: 100,

})

// 监听 store 中 selectedRepository 的变化
watch(() => store.selectedRepository, async (newValue) => {
  if (newValue) {
    form.repository = newValue
    await loadBranches(newValue)
  }
})

const searchResults = ref({
  count: 0,
  next: null,
  previous: null,
  results: [],
})
const handleSizeChange = (val: number) => {
  form.page_size = val
  currentPage.value = 1
  onSubmit()
}
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  onSubmit()
}

const onSubmit = async () => {
  try {
    const formattedData = {
      ...form,
      start_date: form.start_date && form.start_time ? new Date(form.start_date.setHours(form.start_time.getHours(), form.start_time.getMinutes())).toISOString() : null,
      end_date: form.end_date && form.end_time ? new Date(form.end_date.setHours(form.end_time.getHours(), form.end_time.getMinutes())).toISOString() : null,
      page: currentPage.value,
      page_size: form.page_size,
    }
    console.log('Submitting:', formattedData)
    const results = await searchCommits(formattedData)
    searchResults.value = results
    console.log('Search results:', results)
  } catch (error) {
    console.error('搜索失败:', error)
    // 这里可以添加错误处理，比如显示一个错误消息
  }
}
</script>