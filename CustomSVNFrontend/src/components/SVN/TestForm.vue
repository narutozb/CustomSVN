<template>
  <el-form :model="form" label-width="auto" style="max-width: 600px">
    <el-form-item label="Search Contents">
      <el-input v-model="form.contents"/>
    </el-form-item>
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
      <el-checkbox-group v-model="form.type">
        <el-checkbox value="Message" name="type">
          Message
        </el-checkbox>
        <el-checkbox value="Username" name="type">
          Username
        </el-checkbox>
        <el-checkbox value="Revision" name="type">
          Revision
        </el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="onSubmit">Create</el-button>
      <el-button>Cancel</el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import { computed, reactive, ref, watch } from 'vue'
import { onMounted } from 'vue'
import { useRepositoriesStore } from "@/store/repositories"
import { fetchBranches } from '@/services/svn_api'

const store = useRepositoriesStore()
const branches = ref([])

// 设置默认的开始和结束时间
const setDefaultDates = () => {
  const now = new Date()
  const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

  form.end_date = now
  form.end_time = now
  form.start_date = yesterday
  form.start_time = yesterday
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
  console.log('选中的仓库ID:', value)
  const selectedRepo = store.repositories.find(repo => repo.id === value)
  console.log('选中的仓库详情:', selectedRepo)
  await loadBranches(value)
}

const setDefaultBranches = () => {
  const trunkBranch = branches.value.find(branch => branch.name === '/trunk')
  form.branches = trunkBranch ? [trunkBranch.id] : []
}

const form = reactive({
  contents: '',
  repository: computed({
    get: () => store.selectedRepository,
    set: (value) => store.setSelectedRepository(value)
  }),
  branches: [],
  start_date: null as Date | null,
  start_time: null as Date | null,
  end_date: null as Date | null,
  end_time: null as Date | null,
  exact_search: false,
  type: [],
})

// 监听 store 中 selectedRepository 的变化
watch(() => store.selectedRepository, async (newValue) => {
  if (newValue) {
    form.repository = newValue
    await loadBranches(newValue)
  }
})

const onSubmit = () => {
  console.log('submit!')
  console.log(form)
}
</script>