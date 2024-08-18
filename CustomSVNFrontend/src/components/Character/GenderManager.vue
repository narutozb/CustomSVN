<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu
          :default-active="activeMenuItem"
          class="el-menu-vertical-demo"
          @select="handleSelect"
      >
        <el-menu-item index="home">
          <el-icon><icon-menu /></el-icon>
          <span>Home</span>
        </el-menu-item>
        <el-menu-item v-for="item in menuItems" :key="item.name" :index="item.name">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <component :is="currentView" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, shallowRef, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Menu as IconMenu, User, PriceTag } from '@element-plus/icons-vue'
import CharacterManager from '@/components/Character/CharacterManager.vue'
import TagManager from '@/components/Character/TagManager.vue'
import CharacterHome from '@/components/Character/CharacterHome.vue'

const router = useRouter()
const activeMenuItem = ref('home')
const currentView = shallowRef(CharacterHome)

const menuItems = [
  { name: 'characters', label: 'Characters', icon: User, component: CharacterManager },
  { name: 'tags', label: 'Tags', icon: PriceTag, component: TagManager },
  // 可以在这里添加更多菜单项
]

const handleSelect = (key: string) => {
  activeMenuItem.value = key
  if (key === 'home') {
    currentView.value = CharacterHome
  } else {
    const selectedItem = menuItems.find(item => item.name === key)
    if (selectedItem) {
      currentView.value = selectedItem.component
    }
  }
  router.push({ name: key })
}

onMounted(() => {
  const currentRoute = router.currentRoute.value.name as string
  if (currentRoute && currentRoute !== 'home') {
    handleSelect(currentRoute)
  }
})
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
</style>