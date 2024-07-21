<template>
  <el-header class="app-header">
    <div class="header-left">
<!--      <img src="@/assets/logo2.webp" alt="Logo" class="logo"/>-->
      <h1 class="site-title">Custom SVN</h1>
    </div>
    <el-menu
        mode="horizontal"
        :default-active="activeIndex"
        class="header-menu"
        @select="handleSelect"
        router
    >
                  <el-menu-item index="1" route="/" >Home</el-menu-item>
      <!--            <el-menu-item index="2" route="/character" >CharacterManager</el-menu-item>-->
      <!--            <el-menu-item index="3" route="/task">Task</el-menu-item>-->
      <el-menu-item index="4" route="/svn">SVN</el-menu-item>
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
import {ElMessage} from 'element-plus'
import {ArrowDown} from '@element-plus/icons-vue'
import {useUserStore} from '@/store/user'
import {ref, computed, onMounted, watch} from 'vue'
import {useRouter, useRoute} from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

const activeIndex = ref('1')


const isLoggedIn = computed(() => !!userStore.user)
const username = computed(() => userStore.user?.username || '')
const route = useRoute()

const setActiveIndex = () => {
  const path = route.path
  switch (path) {
    case '/':
      activeIndex.value = '1'
      break
    case '/character':
      activeIndex.value = '2'
      break
    case '/task':
      activeIndex.value = '3'
      break
    case '/svn':
      activeIndex.value = '4'
      break
    default:
      if (path.startsWith('/svn')) {
        activeIndex.value = '4'
      } else if (path.startsWith('/character')) {
        activeIndex.value = '2'
      } else if (path.startsWith('/task')) {
        activeIndex.value = '3'
      } else {
        activeIndex.value = ''
      }
  }
}


const handleSelect = (key: string, keyPath: string[]) => {
  // 由于添加了 router 属性，这个函数可以简化或移除
  console.log(key, keyPath);
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
      ElMessage.success('Successes to logout')
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