// src/services/interfaces.ts
export interface SearchCommitsData {
    page: number;
    page_size: number;
    // 添加其他必要的属性
}

export interface Branch {
    id: string;
    name: string;
}

export interface Repository {
    id: string;
    name: string;
    // 添加其他必要的属性
}

export interface Commit {
    revision: string;
    author: string;
    date: string;
    message: string;
    file_changes: Array<{
        path: string;
        action: string;
        kind: string;
    }>;
}

export interface User {
    username: string;
    // 添加其他用户属性
}


export interface Character {
    id?: number;
    name: string;
    character_id: string;
    description?: string;
    height?: number;
    gender?: number;
    race?: number;
    tags?: number[];
    thumbnails?: Array<{ id: number; name: string; image: string }>;

}

export interface SearchCommitsResponse {
    results?: any[];
    count?: number;
    next?: string | null;
    previous?: string | null;
    error?: string;
}

export interface UploadFile {
    name: string;
    url: string;
    status?: string;
    uid?: string;
    raw?: File;
}

