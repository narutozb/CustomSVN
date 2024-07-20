// router/index.ts
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router';
import Home from '@/views/HomeView.vue';
import Login from '@/views/LoginView.vue';
import {useUserStore} from '@/store/user';
import Layout from "@/views/LayoutView.vue";
import SVNView from "@/views/svn/SVNView.vue"
import CommitSearch from "@/components/SVN/CommitSearch.vue";

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        component: Layout,
        meta: {requiresAuth: true},
        children: [
            {
                path: '',
                component: Home
            },
            {
                path: '/svn',
                contents: 'SVN',
                component: SVNView,
                children: [
                    {
                        path: 'commits',
                        contents: 'CommitSearch',
                        component: CommitSearch,
                    }
                ]
            },
        ],
    },
    {path: '/login', component: Login},
    // 添加其他路由...
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore();
    const isAuthenticated = await userStore.checkAuth();

    if (to.path === '/login') {
        if (isAuthenticated) {
            next('/');
        } else {
            next();
        }
    } else if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!isAuthenticated) {
            next('/login');
        } else {
            next();
        }
    } else {
        next();
    }
});

export default router;