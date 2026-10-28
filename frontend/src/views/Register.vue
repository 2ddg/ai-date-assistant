<template>
  <AuthShell
    label="JOIN US"
    index="02 / 02"
    kicker="START HERE"
    :heading="'爱是需要练习的，\n不是等来的。'"
    :lead="'写下你的第一条对话，\n让 AI 军师陪你拆解心动、犹豫，和那些说不出口的话。'"
  >
    <div class="auth-head">
      <p class="page-kicker">NEW ACCOUNT</p>
      <h2>创建账号。</h2>
      <p>不需要完美的人设，只需要一个开始。</p>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="auth-form"
      @submit.prevent="handleRegister"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="form.username"
          placeholder="至少 3 个字符"
          size="large"
          :prefix-icon="User"
          autocomplete="username"
        />
      </el-form-item>
      <el-form-item label="昵称（选填）" prop="nickname">
        <el-input
          v-model="form.nickname"
          placeholder="想被怎么称呼"
          size="large"
          :prefix-icon="Star"
        />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="至少 6 位"
          size="large"
          :prefix-icon="Lock"
          show-password
          autocomplete="new-password"
          @keyup.enter="handleRegister"
        />
      </el-form-item>

      <el-button
        type="primary"
        size="large"
        :loading="loading"
        class="submit-btn"
        @click="handleRegister"
      >
        创建账号
        <el-icon class="el-icon--right"><Right /></el-icon>
      </el-button>
    </el-form>

    <div class="auth-footer">
      <span>已经有账号？</span>
      <router-link to="/login" class="link">直接登录</router-link>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Star, Right } from '@element-plus/icons-vue'
import { register } from '../api/auth.js'
import { useUserStore } from '../stores/user.js'
import AuthShell from '../components/AuthShell.vue'

const router = useRouter()
const userStore = useUserStore()

const form = ref({ username: '', password: '', nickname: '' })
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少 3 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
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
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-head {
  margin-bottom: 26px;
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
  margin-bottom: 14px;
}

.auth-form :deep(.el-form-item__label) {
  padding-bottom: 6px;
  font-size: 11.5px;
  letter-spacing: 0.4px;
}

.submit-btn {
  width: 100%;
  height: 46px;
  margin-top: 10px;
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
