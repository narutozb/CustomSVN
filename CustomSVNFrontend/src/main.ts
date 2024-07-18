import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from '@/App.vue'
import router from '@/router'
// import 'bootstrap/dist/css/bootstrap.css'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引用懒加载指令插件并且注册

import { lazyPlugin } from "@/directives";

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(lazyPlugin);
app.use(ElementPlus)
app.mount('#app')
