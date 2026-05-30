import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/projects',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' },
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/Project.vue'),
    meta: { title: '项目管理' },
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '项目详情' },
  },
  {
    path: '/agent-hub',
    name: 'AgentHub',
    component: () => import('@/views/AgentHub.vue'),
    meta: { title: '大熊AI智能体' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
