// main.ts
import {createApp} from "vue";
import {createPinia} from "pinia";

import App from "@/App.vue";
import router from "@/router";

import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import {registerGlobalProperties} from "@/utils/filters";
import ja from 'element-plus/es/locale/lang/ja'

const app = createApp(App);
registerGlobalProperties(app);

app.use(createPinia());
app.use(router);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.use(ElementPlus, {
    locale: ja,
});


app.mount("#app");
