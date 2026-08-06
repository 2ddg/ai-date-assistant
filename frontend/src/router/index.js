import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/chat',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
        meta: { title: 'AI 对话' },
      },
      {
        path: 'outfit',
        name: 'Outfit',
        component: () => import('../views/Outfit.vue'),
        meta: { title: '穿搭评价' },
      },
      {
        path: 'spots',
        name: 'Spots',
        component: () => import('../views/Spots.vue'),
        meta: { title: '约会地点' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const store = useUserStore()
  if (to.meta.requiresAuth && !store.isLoggedIn) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && store.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
