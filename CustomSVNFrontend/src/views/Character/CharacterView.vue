<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu
          :default-active="activeIndex"
          class="el-menu-vertical-demo"
          @select="handleSelect"
      >
        <template v-for="group in menuGroups" :key="group.name">
          <el-sub-menu :index="group.name">
            <template #title>
              <el-icon>
                <component :is="group.icon"/>
              </el-icon>
              <span>{{ group.label }}</span>
            </template>
            <el-menu-item
                v-for="item in group.items"
                :key="item.name"
                :index="item.name"
            >
              <router-link
                  :to="{ name: item.routeName }"
                  custom
                  v-slot="{ navigate, href }"
              >
                <a
                    :href="href"
                    @click="navigate"
                    @click.middle.prevent="openInNewTab(item.routeName)"
                >
                  <el-icon>
                    <component :is="item.icon"/>
                  </el-icon>
                  <span>{{ item.label }}</span>
                </a>
              </router-link>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>
    <el-main>
      <RouterView/>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {RouterView, useRouter} from 'vue-router'
import {ElContainer, ElAside, ElMain, ElMenu, ElMenuItem, ElSubMenu} from 'element-plus'
import {Menu as IconMenu, Document, User, PriceTag, Setting} from '@element-plus/icons-vue'

interface MenuItem {
  name: string;
  label: string;
  icon: any;
  routeName: string;
}

interface MenuGroup {
  name: string;
  label: string;
  icon: any;
  items: MenuItem[];
}

const menuGroups: MenuGroup[] = [
  {
    name: 'CharacterManagement',
    label: 'CharacterManagement',
    icon: User,
    items: [
      {name: 'characters', label: 'Characters', icon: User, routeName: 'Characters'},
      {name: 'tags', label: 'Tags', icon: PriceTag, routeName: 'Tags'},
    ]
  },
  {
    name: 'settings',
    label: 'Settings',
    icon: Setting,
    items: [
      // { name: 'general', label: 'General Settings', icon: Setting, routeName: 'GeneralSettings' },
      // 可以添加更多设置相关的菜单项
    ]
  },
  // 可以添加更多分组
]

const router = useRouter()
const activeIndex = ref(menuGroups[0].items[0].name)

const handleSelect = (key: string) => {
  activeIndex.value = key
}

const openInNewTab = (routeName: string) => {
  const route = router.resolve({name: routeName})
  window.open(route.href, '_blank')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #545c64;
}

.el-menu {
  height: 100%;
  border-right: none;
}

.el-menu-item a {
  display: flex;
  align-items: center;
  color: inherit;
  text-decoration: none;
  width: 100%;
  height: 100%;
}

.el-menu-item a .el-icon {
  margin-right: 5px;
}
</style>