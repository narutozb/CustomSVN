// src/services/character_api.ts
import api from "@/services/api";
import type {Character} from "@/services/interfaces";
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

    fetchTags: async (): Promise<Array<{ id: number; name: string }>> => {
        const response = await api.get('/api/character/tags/');
        return response.data.results;
    },

    createCharacter: async (character: FormData): Promise<Character> => {
        const response = await api.post('/api/character/characters/', character, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    updateCharacter: async (id: number, character: FormData): Promise<Character> => {
        const response = await api.put(`/api/character/characters/${id}/`, character, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    deleteCharacter: async (id: number): Promise<void> => {
        await api.delete(`/api/character/characters/${id}/`);
    }
};