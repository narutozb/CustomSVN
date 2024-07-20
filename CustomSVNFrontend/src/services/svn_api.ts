// src/services/svn_api.ts
import api from "@/services/api";

export const fetchBranches = async (repositoryId: string) => {
    try {
        const response = await api.get(`api/svn/branches/?repository__id=${repositoryId}`);
        console.log(`api/branches/?repository__id=${repositoryId}`)
        return response.data.results; // 返回结果，而不是直接修改 branches
    } catch (error) {
        console.error('获取分支列表失败:', error);
        throw error; // 抛出错误，以便调用者可以处理
    }
}