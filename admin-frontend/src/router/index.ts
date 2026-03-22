import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UserManagementView.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'rag',
        name: 'RAG',
        component: () => import('@/views/RagManagementView.vue'),
        meta: { title: 'RAG文档管理', icon: 'Document' }
      },
      {
        path: 'prompts',
        name: 'Prompts',
        component: () => import('@/views/PromptManagementView.vue'),
        meta: { title: '提示词管理', icon: 'EditPen' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '管理后台'} - 旅游助手`
  
  const authStore = useAuthStore()
  
  if (!to.meta.public && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
