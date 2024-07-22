// src/store/repositories.ts
import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from "@/services/api"
import {ElMessage} from "element-plus"
import type {Repository} from "@/services/interfaces";


export const useRepositoriesStore = defineStore('repositories', () => {
    const repositories = ref<Repository[]>([])
    const selectedRepository = ref<string>('')

    const fetchRepositories = async () => {
        try {
            const params = {}
            const response = await api.get<{ results: Repository[] }>('api/svn/repositories/', {params})
            repositories.value = response.data.results
            // ElMessage.success('查询成功')
            if (repositories.value.length > 0) {
                selectedRepository.value = repositories.value[0].id
            }
        } catch (error) {
            console.error('获取仓库列表失败:', error)
            ElMessage.error('获取仓库列表失败')
        }
    }

    const setSelectedRepository = (id: string) => {
        selectedRepository.value = id
    }

    return {repositories, selectedRepository, fetchRepositories, setSelectedRepository}
})