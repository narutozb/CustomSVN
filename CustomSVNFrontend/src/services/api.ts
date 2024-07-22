import axios from 'axios';

const api = axios.create({
    // 测试http://localhost:8000
    baseURL: '/',  // 根据您的Django服务器地址调整 TODO:build时修改为/
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;