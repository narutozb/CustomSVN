<template>
  <div class="character-home">
    <h1>Welcome to Character Management</h1>
    <p>Here you can manage characters, tags, and other related entities.</p>
    <el-row :gutter="20">
      <el-col :span="8" v-for="item in menuItems" :key="item.name">
        <el-card class="box-card" @click="navigateTo(item.name)">
          <template #header>
            <div class="card-header">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
            </div>
          </template>
          <div class="card-content">
            {{ item.description }}
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { User, PriceTag } from '@element-plus/icons-vue'

const router = useRouter()

const menuItems = [
  {
    name: 'characters',
    label: 'Characters',
    icon: User,
    description: 'Manage character profiles including their attributes and relationships.'
  },
  {
    name: 'tags',
    label: 'Tags',
    icon: PriceTag,
    description: 'Organize and categorize characters with customizable tags.'
  },
  // 可以在这里添加更多菜单项
]

const navigateTo = (name: string) => {
  router.push({ name })
}
</script>

<style scoped>
.character-home {
  padding: 20px;
}

.box-card {
  cursor: pointer;
  transition: all 0.3s;
}

.box-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header .el-icon {
  margin-right: 10px;
}

.card-content {
  font-size: 14px;
  color: #666;
}
</style>