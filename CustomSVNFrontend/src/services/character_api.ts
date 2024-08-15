// src/services/character_api.ts
import api from "@/services/api";
import type {Character, Tag} from "@/services/interfaces";


interface TableField {
    key: string;
    label: string;
    sortable: boolean;
    editable: boolean;
}

interface EditField {
    key: string;
    label: string;
    type: 'text' | 'textarea' | 'switch';
    required: boolean;
}

interface FilterOptions {
    search_fields: string[];
    ordering_fields: string[];
    table_fields: TableField[];
    edit_fields: EditField[];
}


export interface FetchTagsParams {
    page: number;
    page_size: number;
    search?: string;
    ordering?: string;

    [key: string]: any;  // 用于处理动态过滤器
}

interface FetchTagsResponse {
    pagination: {
        total_items: number;
        total_pages: number;
        current_page: number;
        next: string | null;
        previous: string | null;
    };
    results: Tag[];
}

export const characterApi = {
    fetchCharacters: async (): Promise<Character[]> => {
        const response = await api.get('/api/character/characters/');
        return response.data.results || [];
    },

    fetchGenders: async (): Promise<Array<{ id: number; name: string }>> => {
        const response = await api.get('/api/character/genders/');
        return response.data.results;
    },

    fetchRaces: async (): Promise<Array<{ id: number; name: string }>> => {
        const response = await api.get('/api/character/races/');
        return response.data.results;
    },

    createCharacter: async (character: FormData): Promise<Character> => {
        const response = await api.post('/api/character/characters/', character, {
            headers: {'Content-Type': 'multipart/form-data'}
        });
        return response.data;
    },

    updateCharacter: async (id: number, character: FormData): Promise<Character> => {
        const response = await api.put(`/api/character/characters/${id}/`, character, {
            headers: {'Content-Type': 'multipart/form-data'}
        });
        return response.data;
    },

    deleteCharacter: async (id: number): Promise<void> => {
        await api.delete(`/api/character/characters/${id}/`);
    },
    fetchMaxThumbnails: async (): Promise<{ max_thumbnails: number }> => {
        const response = await api.get('/api/character/max-thumbnails/');
        return response.data;
    },
    // Gender
    createGender: async (gender: { name: string }): Promise<{ id: number; name: string }> => {
        const response = await api.post('/api/character/genders/', gender);
        return response.data;
    },
    updateGender: async (id: number, gender: { name: string }): Promise<{ id: number; name: string }> => {
        const response = await api.put(`/api/character/genders/${id}/`, gender);
        return response.data;
    },
    deleteGender: async (id: number): Promise<void> => {
        await api.delete(`/api/character/genders/${id}/`);
    },

// Race
    createRace: async (race: { name: string }): Promise<{ id: number; name: string }> => {
        const response = await api.post('/api/character/races/', race);
        return response.data;
    },
    updateRace: async (id: number, race: { name: string }): Promise<{ id: number; name: string }> => {
        const response = await api.put(`/api/character/races/${id}/`, race);
        return response.data;
    },
    deleteRace: async (id: number): Promise<void> => {
        await api.delete(`/api/character/races/${id}/`);
    },

// Tag
    fetchTags: async (params: FetchTagsParams): Promise<FetchTagsResponse> => {
        const response = await api.get('/api/character/_charactertags/query/', {params});
        return response.data;
    },

    createTag: async (tag: Omit<Tag, 'id'>): Promise<Tag> => {
        const response = await api.post('/api/character/_charactertags/command/', tag);
        return response.data;
    },

    updateTag: async (id: number, tag: Omit<Tag, 'id'>): Promise<Tag> => {
        const response = await api.put(`/api/character/tags/${id}/`, tag);
        return response.data;
    },
    deleteTag: async (id: number): Promise<void> => {
        await api.delete(`/api/character/tags/${id}/`);
    },
    fetchTagFilterOptions: async (): Promise<FilterOptions> => {
        const response = await api.get('/api/character/_charactertags/query/filter_options/');
        return response.data;
    },
};