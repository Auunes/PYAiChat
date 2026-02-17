import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
  },
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('@/views/Admin/Layout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Admin/Dashboard.vue'),
      },
      {
        path: 'channels',
        name: 'Channels',
        component: () => import('@/views/Admin/Channels.vue'),
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/Admin/Logs.vue'),
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Admin/Settings.vue'),
      },
    ],
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/Admin/Login.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const adminToken = localStorage.getItem('admin_token')

  if (to.meta.requiresAdmin && !adminToken) {
    next('/admin/login')
  } else {
    next()
  }
})

export default router
