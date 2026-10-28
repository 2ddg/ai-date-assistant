<template>
  <div class="app-shell">
    <div v-if="menuOpen" class="sidebar-scrim" @click="menuOpen = false" />

    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="sidebar-glow" />

      <header class="brand">
        <span class="brand-mark">✳</span>
        <div class="brand-copy">
          <strong>AI 约会助手</strong>
          <span>THE LOVE LAB</span>
        </div>
      </header>

      <p class="nav-label">WORKSPACE</p>
      <nav class="nav">
        <router-link
          v-for="(item, index) in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
          @click="menuOpen = false"
        >
          <span class="nav-index">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="nav-icon"><el-icon><component :is="item.icon" /></el-icon></span>
          <span class="nav-copy">
            <strong>{{ item.label }}</strong>
            <em>{{ item.desc }}</em>
          </span>
        </router-link>
      </nav>

      <div class="sidebar-note">
        <span class="note-mark">✳</span>
        <p>今天也要好好爱人，<br />更要好好爱自己。</p>
        <span class="note-foot">A NOTE TO SELF</span>
      </div>

      <footer class="sidebar-foot">
        <div class="user-chip">
          <span class="user-avatar">{{ initial }}</span>
          <div>
            <strong>{{ userStore.username || '旅人' }}</strong>
            <span>正在练习中</span>
          </div>
        </div>
        <button type="button" class="logout-btn" title="退出登录" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
        </button>
      </footer>
    </aside>

    <div class="main-wrap">
      <header class="topbar">
        <div class="topbar-left">
          <button type="button" class="menu-btn" @click="menuOpen = true">
            <el-icon><Expand /></el-icon>
          </button>
          <div>
            <p class="page-kicker">{{ currentPage.kicker }}</p>
            <h1>{{ currentPage.title }}</h1>
          </div>
        </div>
        <div class="topbar-right">
          <span class="date-chip">{{ dateLabel }}</span>
          <span class="status-dot" />
          <span class="status-text">军师在线</span>
        </div>
      </header>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  ChatLineRound, BrushFilled, LocationFilled, SwitchButton, Expand,
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user.js'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const menuOpen = ref(false)

const navItems = [
  { path: '/chat', label: 'AI 对话', desc: '把心事说给军师听', icon: ChatLineRound, kicker: 'THE CONVERSATION' },
  { path: '/outfit', label: '穿搭评审', desc: '穿对衣服，也穿对自己', icon: BrushFilled, kicker: 'THE LOOK' },
  { path: '/spots', label: '约会地点', desc: '从真实地点开始一场约会', icon: LocationFilled, kicker: 'THE PLACE' },
]

const currentPage = computed(() => {
  return navItems.find((item) => route.path.startsWith(item.path)) || navItems[0]
})

const initial = computed(() => Array.from(userStore.username || '旅')[0])

const dateLabel = computed(() =>
  new Intl.DateTimeFormat('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' }).format(new Date())
)

watch(() => route.path, () => {
  menuOpen.value = false
})

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出', {
      confirmButtonText: '退出',
      cancelButtonText: '再待一会儿',
      type: 'warning',
    })
  } catch {
    return
  }
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  z-index: 40;
  display: flex;
  flex-direction: column;
  width: 252px;
  height: 100vh;
  flex-shrink: 0;
  padding: 26px 18px 20px;
  border-right: 1px solid var(--color-hairline);
  background:
    radial-gradient(380px 320px at -20% 8%, rgba(255, 107, 157, 0.13), transparent 70%),
    linear-gradient(180deg, #1e1014 0%, #130a0d 100%);
  overflow: hidden;
}

.sidebar-glow {
  position: absolute;
  right: -170px;
  bottom: -120px;
  width: 340px;
  height: 340px;
  border: 1px solid rgba(255, 107, 157, 0.1);
  border-radius: 50%;
  pointer-events: none;
}

.sidebar-glow::before {
  content: "";
  position: absolute;
  inset: 54px;
  border: 1px solid rgba(255, 107, 157, 0.06);
  border-radius: 50%;
}

.brand {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px 30px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  background: rgba(255, 107, 157, 0.07);
  color: var(--color-primary);
  font-size: 15px;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-copy strong {
  color: var(--color-ink);
  font-size: 14px;
  font-weight: 600;
}

.brand-copy span {
  color: var(--color-muted-soft);
  font-size: 8px;
  letter-spacing: 2.1px;
}

.nav-label {
  position: relative;
  z-index: 1;
  margin: 0 0 10px;
  padding: 0 10px;
  color: var(--color-muted-soft);
  font-size: 8.5px;
  letter-spacing: 2px;
}

.nav {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 11px;
  border: 1px solid transparent;
  border-radius: 11px;
  color: var(--color-muted);
  transition: all var(--dur-fast) var(--ease-out);
}

.nav-item:hover {
  color: var(--color-body);
  background: rgba(255, 255, 255, 0.035);
}

.nav-item.active {
  color: var(--color-ink);
  border-color: var(--color-hairline);
  background:
    linear-gradient(100deg, rgba(255, 107, 157, 0.12), transparent 78%),
    rgba(255, 255, 255, 0.045);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
}

.nav-item.active::before {
  content: "";
  position: absolute;
  top: 12px;
  bottom: 12px;
  left: -1px;
  width: 2px;
  border-radius: 2px;
  background: var(--color-primary);
}

.nav-index {
  width: 18px;
  color: var(--color-muted-soft);
  font-size: 8.5px;
  letter-spacing: 0.5px;
}

.nav-item.active .nav-index {
  color: var(--color-primary);
}

.nav-icon {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  font-size: 13px;
}

.nav-item.active .nav-icon {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.nav-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.nav-copy strong {
  font-size: 12.5px;
  font-weight: 500;
}

.nav-copy em {
  color: var(--color-muted-soft);
  font-size: 9.5px;
  font-style: normal;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-note {
  position: relative;
  z-index: 1;
  margin: auto 4px 18px;
  padding: 17px 16px 14px;
  border: 1px solid var(--color-hairline);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
}

.note-mark {
  color: var(--color-primary);
  font-size: 12px;
}

.sidebar-note p {
  margin: 9px 0 12px;
  color: var(--color-body);
  font-family: var(--font-serif);
  font-size: 13px;
  line-height: 1.7;
}

.note-foot {
  color: var(--color-muted-soft);
  font-size: 7.5px;
  letter-spacing: 1.7px;
}

.sidebar-foot {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 6px 0;
  border-top: 1px solid var(--color-hairline-soft);
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  flex: 1;
}

.user-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff8db4, #c73b6b);
  color: #1c0d12;
  font-family: var(--font-serif);
  font-size: 14px;
}

.user-chip div {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-chip strong {
  color: var(--color-ink);
  font-size: 11.5px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-chip span:last-child {
  color: var(--color-muted-soft);
  font-size: 9px;
}

.logout-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 8px;
  background: none;
  color: var(--color-muted-soft);
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.logout-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-hairline);
  background: rgba(255, 107, 157, 0.07);
}

.main-wrap {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 34px 18px;
  border-bottom: 1px solid var(--color-hairline-soft);
  background: rgba(24, 14, 17, 0.72);
  backdrop-filter: blur(18px);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.topbar-left h1 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 26px;
  font-weight: 500;
  letter-spacing: -0.4px;
  line-height: 1.2;
  color: var(--color-ink);
}

.topbar-left .page-kicker {
  margin-bottom: 3px;
  font-size: 8.5px;
  letter-spacing: 2px;
}

.menu-btn {
  display: none;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-hairline);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--color-body);
  cursor: pointer;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--color-muted);
  font-size: 10.5px;
}

.date-chip {
  padding: 5px 11px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.025);
  white-space: nowrap;
}

.status-dot {
  width: 5px;
  height: 5px;
  margin-left: 4px;
  border-radius: 50%;
  background: #8fd3b6;
  box-shadow: 0 0 0 3px rgba(143, 211, 182, 0.1);
}

.status-text {
  color: var(--color-muted-soft);
}

.content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 34px 48px;
}

.sidebar-scrim {
  display: none;
}

@media (max-width: 1040px) {
  .sidebar {
    position: fixed;
    left: 0;
    transform: translateX(-100%);
    transition: transform var(--dur-base) var(--ease-out);
    box-shadow: 24px 0 60px rgba(0, 0, 0, 0.4);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-scrim {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 35;
    background: rgba(8, 3, 5, 0.62);
    backdrop-filter: blur(4px);
  }

  .menu-btn {
    display: flex;
  }

  .topbar {
    padding: 16px 22px 14px;
  }

  .content {
    padding: 22px 22px 40px;
  }
}

@media (max-width: 620px) {
  .topbar-right {
    display: none;
  }

  .topbar-left h1 {
    font-size: 22px;
  }

  .content {
    padding: 18px 16px 34px;
  }
}
</style>
