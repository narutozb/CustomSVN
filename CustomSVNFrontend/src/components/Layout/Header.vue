<template>
  <el-header class="app-header">
    <div class="header-left">
      <h1 class="site-title">Custom SVN</h1>
    </div>
    <el-menu
        mode="horizontal"
        :default-active="activeIndex"
        class="header-menu"
        @select="handleSelect"
        router
    >
      <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index" :route="item.route">
        {{ item.text }}
      </el-menu-item>
    </el-menu>

    <div class="header-right">
      <template v-if="isLoggedIn">
        <el-dropdown @command="handleCommand" trigger="click">

          <el-button class="user-dropdown-button">
            <el-icon>
              <User/>
            </el-icon>
            {{ username }}
            <el-icon class="el-icon--right">
              <arrow-down/>
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item divided command="logout">
                <el-icon>
                  <SwitchButton/>
                </el-icon>
                logout
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeIndex = ref('1')

const isLoggedIn = computed(() => !!userStore.user)
const username = computed(() => userStore.user?.username || '')

// 定义菜单项
const menuItems = [
  { index: '1', route: '/', text: 'Home' },
  { index: '2', route: '/character', text: 'CharacterManager' },
  // { index: '3', route: '/task', text: 'Task' },  // 注释掉的菜单项
  { index: '4', route: '/svn', text: 'SVN' },
]

const setActiveIndex = () => {
  const currentPath = route.path
  const matchedRoutes = route.matched.map(record => record.path)

  let bestMatch = ''
  let bestMatchIndex = ''

  menuItems.forEach(item => {
    if (matchedRoutes.includes(item.route) || currentPath.startsWith(item.route)) {
      if (item.route.length > bestMatch.length) {
        bestMatch = item.route
        bestMatchIndex = item.index
      }
    }
  })

  activeIndex.value = bestMatchIndex || ''
}

const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('Successfully logged out')
      router.push('/login')
      break
  }
}

onMounted(() => {
  setActiveIndex()
})

watch(() => route.path, () => {
  setActiveIndex()
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  margin-right: 10px;
}

.site-title {
  font-size: 1.2em;
  margin: 0;
}

.header-menu {
  flex-grow: 1;
  justify-content: flex-start;
}

.el-menu {
  margin-left: 40px;
}

.header-right {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-dropdown-link .el-icon {
  margin-left: 5px;
}
</style>