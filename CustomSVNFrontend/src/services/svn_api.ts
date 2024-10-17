// svn_api.ts
import api from "@/services/api";
import type {
    Branch,
    Commit,
    CommitSearchFilter,
    Repository,
    SearchCommitsData,
    SearchCommitsResponse
} from "@/services/interfaces";

export const fetchBranches = async (repositoryId: string): Promise<Branch[]> => {
    try {
        const response = await api.get(`api/svn/branches_query/?repo_id=${repositoryId}`);
        return response.data.results;
    } catch (error) {
        console.error('Failed to get branch list:', error);
        throw error;
    }
}

export const getBranches = async (params: any): Promise<Branch[]> => {
    try {
        const response = await api.get(`api/svn/branches_query/`, {params});
        return response.data.results;
    } catch (error) {
        console.error('Failed to get branch list:', error);
        throw error;
    }
}

export const getRepositories = async (params: any): Promise<Repository[]> => {
    try {
        const response = await api.get(`api/svn/repositories_query/`, {params});
        return response.data.results;
    } catch (error) {
        console.error('Failed to get repository list:', error);
        throw error;
    }
}

export const searchCommits = async (data: SearchCommitsData): Promise<SearchCommitsResponse> => {
    try {
        // const response = await api.get('api/svn/commits_query/', {params: data});
        const response = await api.get('api/svn/commits_query-highlighted-commits/', {params: data});
        console.log(data)
        return response.data;
    } catch (error: any) {
        console.error('Failed to search commits:', error);
        const errorResponse: SearchCommitsResponse = {
            count: 0,
            next: null,
            previous: null,
            results: [],
        };
        if (error.response && error.response.data && error.response.data.error) {
            (errorResponse as any).error = error.response.data.error;
        } else {
            (errorResponse as any).error = 'Failed to search commits, please try again later';
        }
        return errorResponse;
    }
}

export const getCommitDetail = async (commitId: number) => {
    try {
        const response = await api.get(`api/svn/_commits/commit-details/${commitId}/`);
        console.log(response.data)
        return response.data;
    } catch (error) {
        console.error('Failed to get commit details:', error);
        throw error;
    }
}


export const getFileChangeDetail = async (fileChangeId: number) => {
    try {
        const response = await api.get(`api/svn/_file_changes/${fileChangeId}`);
        return response.data;
    } catch (error) {
        console.error('Failed to get file change details:', error);
        throw error;
    }
}

export const getCommitDetailsByChangeFile = async (fileChangeId: number) => {
    try {
        const response = await api.get(`api/svn/file_changes_query/${fileChangeId}/file_change_details`);
        return response.data;
    } catch (error) {
        console.error('Failed to get file change details:', error);
        throw error;
    }
}

export const getRelatedCommits = async (fileChangeId: number | string): Promise<Commit[]> => {
    try {
        const response = await api.get(`api/svn/file_changes_query/${fileChangeId}/get_commits_by_self_path/`);
        if (response.data && response.data.results) {
            return response.data.results;
        }
        return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
        console.error('Failed to get related commits:', error);
        throw error;
    }
}

export const getAuthors = async (params: any): Promise<string[]> => {
    try {
        const response = await api.get(`api/svn/repositories_query/authors`, {params: params});
        console.log(`api/svn/repositories_query/authors`)
        return response.data.results;
    } catch (error) {
        console.error('Failed to get branch list:', error);
        throw error;
    }
}


export const getCommitSearchFilterData = async (pk: number | string): Promise<CommitSearchFilter> => {
    try {
        const response = await api.get(`api/svn/repositories_query/${pk}/commit_search_filter/`,);
        return response.data;
    } catch (error) {
        console.error('Failed to get branch list:', error);
        throw error;
    }
}