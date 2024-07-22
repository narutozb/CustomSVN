<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2 class="login-title">Login</h2>
      </template>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" @submit.prevent="handleSubmit">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="Username">
            <template #prefix>
              <el-icon>
                <User/>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="Password" show-password>
            <template #prefix>
              <el-icon>
                <Lock/>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="login-button">Login</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';
import { useRouter } from 'vue-router'; // 添加这行
import type { FormInstance } from 'element-plus';

const userStore = useUserStore();
const router = useRouter(); // 添加这行
const loginFormRef = ref<FormInstance>();
const loading = ref(false);

const loginForm = reactive({
  username: '',
  password: '',
});

const rules = {
  username: [{ required: true, message: 'Input username', trigger: 'blur' }],
  password: [{ required: true, message: 'Input password', trigger: 'blur' }],
};

// 修改 handleSubmit 函数
const handleSubmit = async () => {
  if (!loginFormRef.value) return;

  try {
    loading.value = true;
    await loginFormRef.value.validate();
    await userStore.login(loginForm.username, loginForm.password);

    // 登录成功后，检查是否有重定向 URL
    const redirectUrl = localStorage.getItem('redirectUrl');
    if (redirectUrl) {
      localStorage.removeItem('redirectUrl');
      router.push(redirectUrl);
    } else {
      router.push('/');
    }

    ElMessage.success('Login successful');
  } catch (error) {
    console.error('Login failed:', error);
    ElMessage.error('Login failed. Please check your credentials.');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 350px;
}

.login-title {
  text-align: center;
  font-weight: bold;
}

.login-button {
  width: 100%;
}
</style>