import api from "@/services/api";

export const characterApi = {
    fetchCharacters: async () => {
        const response = await api.get('/api/character/characters/');
        return response.data.results || [];  // 返回结果数组，如果不存在则返回空数组
    },

    fetchGenders: async () => {
        const response = await api.get('/api/character/genders/');
        return response.data.results;
    },

    fetchRaces: async () => {
        const response = await api.get('/api/character/races/');
        return response.data.results;
    },

    fetchTags: async () => {
        const response = await api.get('/api/character/tags/');
        return response.data.results;
    },

    createCharacter: async (character: any) => {
        const response = await api.post('/api/character/characters/', character);
        return response.data.results;
    },

    updateCharacter: async (id: number, character: any) => {
        const response = await api.put(`/api/character/characters/${id}/`, character);
        return response.data.results;
    },

    deleteCharacter: async (id: number) => {
        await api.delete(`/api/character/characters/${id}/`);
    }
};