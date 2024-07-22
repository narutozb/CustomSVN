import { defineStore } from 'pinia';
import api from '@/services/api';
import router from '@/router';

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        token: null,
    }),
    actions: {
        async login(username: string, password: string) {
            try {
                const response = await api.post('api/user/login/', { username, password });
                this.token = response.data.access;
                localStorage.setItem('access_token', response.data.access);
                localStorage.setItem('refresh_token', response.data.refresh);
                await this.fetchUserInfo();
                router.push('/');
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        },
        async logout() {
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                await api.post('api/user/logout/', { refresh_token: refreshToken });
            } catch (error) {
                console.error('Logout failed:', error);
            } finally {
                this.user = null;
                this.token = null;
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                router.push('/login');
            }
        },
        async fetchUserInfo() {
            try {
                const response = await api.get('api/user/me/');
                this.user = response.data;
            } catch (error) {
                console.error('Failed to fetch user info:', error);
                throw error;
            }
        },
        async checkAuth() {
            if (this.user) return true;
            const token = localStorage.getItem('access_token');
            if (!token) return false;
            try {
                await this.fetchUserInfo();
                return true;
            } catch (error) {
                console.error('Auth check failed:', error);
                this.user = null;
                this.token = null;
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                return false;
            }
        },
    },
});