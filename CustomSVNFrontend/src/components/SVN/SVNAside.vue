<template>
  <el-button type="primary" style="margin-left: 16px" @click="drawer = true">
    SVN Navigation
  </el-button>
  <el-drawer v-model="drawer" title="Navigation" :with-header="true" size="80%">
    <div class="drawer-content">
      <div class="menu-section">
        <el-menu
            default-active="1"
            class="el-menu-vertical-demo"
            @select="handleSelect"
            router
        >
          <el-menu-item index="1" route="/">
            <el-icon>
              <icon-menu/>
            </el-icon>
            <span>Home</span>
          </el-menu-item>
          <el-menu-item index="2" route="/svn/commits">
            <el-icon>
              <document/>
            </el-icon>
            <span>SVN Commits</span>
          </el-menu-item>
          <el-sub-menu index="3">
            <template #title>
              <el-icon>
                <location/>
              </el-icon>
              <span>Other Options</span>
            </template>
            <el-menu-item index="3-1" route="/function" disabled>Option 1</el-menu-item>
            <el-menu-item index="3-2" route="/option2" disabled>Option 2</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </div>
      <div class="content-section">
        <h2>SVN Navigation</h2>
        提供SVN查询功能

      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import {ref} from 'vue'
import {Document, Location} from '@element-plus/icons-vue'

const drawer = ref(false)

const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
  drawer.value = false  // 选择菜单项后关闭抽屉
}
</script>

<style scoped>
.drawer-content {
  display: flex;
  height: 100%;
}

.menu-section {
  width: 200px;
  border-right: 1px solid #e6e6e6;
}

.content-section {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.box-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}
</style>