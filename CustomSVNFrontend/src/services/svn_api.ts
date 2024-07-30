// src/services/svn_api.ts
import api from "@/services/api";
import type {Branch, Commit, FileChange, SearchCommitsData, SearchCommitsResponse} from "@/services/interfaces";
import type {Ref, UnwrapRef} from "vue";
import type {CancelToken} from "axios";
import axios from "axios";

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


export const searchCommits = async (data: SearchCommitsData, cancelToken?: CancelToken): Promise<SearchCommitsResponse> => {
    try {
        const response = await api.post('api/svn/_commits/search/', data, {
            params: {
                page: data.page,
                page_size: data.page_size
            },
            cancelToken // 添加这一行
        });
        return response.data;
    } catch (error: any) {
        if (axios.isCancel(error)) {
            console.log('Request canceled', error.message);
            return { results: [], count: 0, next: null, previous: null };
        }
        console.error('搜索提交失败:', error);
        if (error.response && error.response.data) {
            return {error: error.response.data.error || '搜索提交失败'};
        }
        return {error: '搜索提交失败，请稍后重试'};
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


export const getFileChangeDetail = async (fileChangeId: number | null) => {
    try {
        const response = await api.get(`api/svn/file_changes/${fileChangeId}/`);
        return response.data;
    } catch (error) {
        console.error('获取提交详情失败:', error);
        throw error;
    }
}

export const getRelatedCommits = async (filePath: string): Promise<Commit[]> => {
    try {
        const response = await api.get(`api/svn/_commits/by-file-path/`, {params: {path: filePath}});
        // 检查响应是否包含 results 字段（分页响应的常见结构）
        if (response.data && response.data.results) {
            return response.data.results;
        }
        // 如果没有 results 字段，假设整个响应就是提交数组
        return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
        console.error('获取相关提交失败:', error);
        throw error;
    }
}