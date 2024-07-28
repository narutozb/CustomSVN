// src/services/svn_api.ts
import api from "@/services/api";
import type {Branch, SearchCommitsData, SearchCommitsResponse} from "@/services/interfaces";

export const fetchBranches = async (repositoryId: string): Promise<Branch[]> => {
    try {
        const response = await api.get(`api/svn/branches/?repository__id=${repositoryId}`);
        console.log(`api/branches/?repository__id=${repositoryId}`)
        return response.data.results; // 返回结果，而不是直接修改 branches
    } catch (error) {
        console.error('获取分支列表失败:', error);
        throw error; // 抛出错误，以便调用者可以处理
    }
}


export const searchCommits = async (data: SearchCommitsData): Promise<SearchCommitsResponse> => {
    try {
        const response = await api.post('api/svn/_commits/search/', data, {
            params: {
                page: data.page,
                page_size: data.page_size
            }
        });
        return response.data;
    } catch (error: any) {
        console.error('搜索提交失败:', error);
        if (error.response && error.response.data) {
            return { error: error.response.data.error || '搜索提交失败' };
        }
        return { error: '搜索提交失败，请稍后重试' };
    }
}

export const getCommitDetail = async (commitId: number) => {
    try {
        const response = await api.get(`api/svn/_commits/commit-details/${commitId}/`);
        return response.data;
    } catch (error) {
        console.error('获取提交详情失败:', error);
        throw error;
    }
}