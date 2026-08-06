<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2 class="auth-title">
        <el-icon :size="32" color="#ff6b9d"><ChatDotRound /></el-icon>
        AI 约会助手
      </h2>
      <p class="auth-subtitle">创建你的恋爱军师账号</p>

      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名（至少3字符）"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input
            v-model="form.nickname"
            placeholder="昵称（选填）"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（至少6位）"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleRegister"
          style="width: 100%"
        >
          注册
        </el-button>
      </el-form>

      <div class="auth-footer">
        已有账号？
        <router-link to="/login" class="link">直接登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { register } from '../api/auth.js'
import { useUserStore } from '../stores/user.js'

const router = useRouter()
const userStore = useUserStore()

const form = ref({ username: '', password: '', nickname: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const formRef = ref(null)
const loading = ref(false)

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const data = await register(form.value.username, form.value.password, form.value.nickname)
    userStore.setAuth(data.token, data.username)
    ElMessage.success('注册成功！')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #feca57 0%, #ff6b9d 100%);
}

.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.auth-title {
  text-align: center;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.auth-subtitle {
  text-align: center;
  color: #909399;
  margin: 0 0 30px;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  color: #909399;
}

.link {
  color: #ff6b9d;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
