// router/index.ts
import {createRouter, createWebHistory} from 'vue-router';
import type {RouteRecordRaw} from "vue-router";
import {useUserStore} from '@/store/user';
import Home from '@/views/HomeView.vue';
import Login from '@/views/LoginView.vue';
import Layout from "@/views/LayoutView.vue";
import SVNView from "@/views/svn/SVNView.vue"
import CommitDetail from "@/components/SVN/CommitDetail.vue";
import CommitSearchView from "@/views/svn/CommitSearchView.vue";
import CharacterView from "@/views/Character/CharacterView.vue";
import CharacterManager from "@/components/Character/CharacterManager.vue";
import FileChangeDetail from "@/components/SVN/FileChangeDetail.vue";
import GenderManager from "@/components/Character/GenderManager.vue";
import RaceManager from "@/components/Character/RaceManager.vue";
import TagManager from "@/components/Character/TagManager.vue";
import CharacterHome from "@/components/Character/CharacterHome.vue";


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
                // contents: 'SVN',
                component: SVNView,
                children: [
                    {
                        path: 'commits',
                        component: CommitSearchView,
                    },
                    {
                        path: 'commits/:id',
                        name: 'CommitDetail',
                        component: CommitDetail
                    },
                    {
                        path: 'file_changes/:id',
                        name: 'FileChangeDetail',
                        component: FileChangeDetail
                    },

                ]
            },
            {
                path: '/character',
                component: CharacterView,
                children: [
                    {
                        path: '',
                        name: 'home',
                        component: CharacterHome
                    },
                    {
                        path: 'characters',
                        name: 'Characters',
                        component: CharacterManager
                    },
                    {
                        path: 'Gender',
                        component: GenderManager
                    },
                    {
                        path: 'Race',
                        component: RaceManager
                    },
                    {
                        name: 'Tags',
                        path: 'tags',
                        component: TagManager
                    },
                ]
            }

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
            // 保存用户尝试访问的 URL
            localStorage.setItem('redirectUrl', to.fullPath);
            next('/login');
        } else {
            next();
        }
    } else {
        next();
    }
});

export default router;