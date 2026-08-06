<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <el-icon :size="28" color="#ff6b9d"><ChatDotRound /></el-icon>
        <span class="app-title">AI 约会助手</span>
      </div>
      <div class="header-right">
        <span class="welcome">你好，{{ userStore.username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="layout-aside">
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#ff6b9d"
        >
          <el-menu-item index="/chat">
            <el-icon><ChatLineRound /></el-icon>
            <span>AI 对话</span>
          </el-menu-item>
          <el-menu-item index="/outfit">
            <el-icon><BrushFilled /></el-icon>
            <span>穿搭评价</span>
          </el-menu-item>
          <el-menu-item index="/spots">
            <el-icon><LocationFilled /></el-icon>
            <span>约会地点</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-header {
  background: linear-gradient(90deg, #ff6b9d, #feca57);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-title {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome {
  color: #fff;
  font-size: 14px;
}

.layout-aside {
  background: #304156;
}

.layout-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
