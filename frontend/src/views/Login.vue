<template>
  <AuthShell
    label="SIGN IN"
    index="01 / 02"
    kicker="WELCOME BACK"
    :heading="'先成为值得被爱的人，\n再遇见爱。'"
    :lead="'一个不替你谈恋爱的 AI 军师：\n帮你看清场合、穿对衣服、选对地点。'"
  >
    <div class="auth-head">
      <p class="page-kicker">THE LOVE LAB</p>
      <h2>欢迎回来。</h2>
      <p>登录你的私人恋爱军师，继续上一次的练习。</p>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="auth-form"
      @submit.prevent="handleLogin"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="form.username"
          placeholder="输入用户名"
          size="large"
          :prefix-icon="User"
          autocomplete="username"
        />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="输入密码"
          size="large"
          :prefix-icon="Lock"
          show-password
          autocomplete="current-password"
          @keyup.enter="handleLogin"
        />
      </el-form-item>

      <el-button
        type="primary"
        size="large"
        :loading="loading"
        class="submit-btn"
        @click="handleLogin"
      >
        进入约会实验室
        <el-icon class="el-icon--right"><Right /></el-icon>
      </el-button>
    </el-form>

    <div class="auth-footer">
      <span>还没有账号？</span>
      <router-link to="/register" class="link">创建一个</router-link>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Right } from '@element-plus/icons-vue'
import { login } from '../api/auth.js'
import { useUserStore } from '../stores/user.js'
import AuthShell from '../components/AuthShell.vue'

const router = useRouter()
const userStore = useUserStore()

const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const formRef = ref(null)
const loading = ref(false)

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const data = await login(form.value.username, form.value.password)
    userStore.setAuth(data.token, data.username)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-head {
  margin-bottom: 28px;
}

.auth-head h2 {
  margin: 0 0 8px;
  font-family: var(--font-serif);
  font-size: 30px;
  font-weight: 500;
  letter-spacing: -0.6px;
  color: var(--color-ink);
}

.auth-head p:last-child {
  margin: 0;
  color: var(--color-muted);
  font-size: 12.5px;
  line-height: 1.7;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.auth-form :deep(.el-form-item__label) {
  padding-bottom: 6px;
  font-size: 11.5px;
  letter-spacing: 0.4px;
}

.submit-btn {
  width: 100%;
  height: 46px;
  margin-top: 8px;
  font-size: 13.5px;
  letter-spacing: 0.5px;
}

.auth-footer {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 22px;
  color: var(--color-muted);
  font-size: 12.5px;
}

.link {
  color: var(--color-primary);
  font-weight: 500;
  border-bottom: 1px solid transparent;
  transition: border-color var(--dur-fast) var(--ease-out);
}

.link:hover {
  border-color: var(--color-primary);
}
</style>
