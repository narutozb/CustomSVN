import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/',  // 根据您的Django服务器地址调整
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;