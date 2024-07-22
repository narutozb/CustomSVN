<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2 class="login-title">登录</h2>
      </template>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" @submit.prevent="handleSubmit">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名">
            <template #prefix>
              <el-icon>
                <User/>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" show-password>
            <template #prefix>
              <el-icon>
                <Lock/>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="login-button">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive} from 'vue';
import {ElMessage, type FormValidateCallback} from 'element-plus';
import {User, Lock} from '@element-plus/icons-vue';
import {useUserStore} from '@/store/user';
import type {FormInstance} from 'element-plus';

const userStore = useUserStore();
const loginFormRef = ref<FormInstance>();
const loading = ref(false);

const loginForm = reactive({
  username: '',
  password: '',
});

const rules = {
  username: [{required: true, message: '请输入用户名', trigger: 'blur'}],
  password: [{required: true, message: '请输入密码', trigger: 'blur'}],
};
// handleSubmit
const handleSubmit = async () => {
  if (!loginFormRef.value) return

  const validateCallback: FormValidateCallback = async (valid) => {
    if (valid) {
      try {
        await userStore.login(loginForm.username, loginForm.password)
        // 登录成功后的逻辑
      } catch (error) {
        // 处理登录失败
        console.error('Login failed:', error)
      }
    } else {
      console.log('Form validation failed')
    }
  }

  await loginFormRef.value.validate(validateCallback)
}
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