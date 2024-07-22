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

// 在 <script> 标签内添加
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