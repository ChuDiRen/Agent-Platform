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
  {
    path: '/test-data-generator',
    name: 'TestDataGenerator',
    component: () => import('@/views/TestDataGenerator.vue'),
    meta: { title: 'AI测试数据生成' },
  },
  {
    path: '/ai-test-cases',
    name: 'AITestCaseAgent',
    component: () => import('@/views/AITestCaseAgent.vue'),
    meta: { title: 'AI接口用例设计助手' },
  },
  {
    path: '/requirement-review',
    name: 'RequirementReviewAssistant',
    component: () => import('@/views/RequirementReviewAssistant.vue'),
    meta: { title: 'AI需求评审助手' },
  },
  {
    path: '/interface-document-analysis',
    name: 'ApiDocumentAnalysis',
    component: () => import('@/views/ApiDocumentAnalysis.vue'),
    meta: { title: 'AI接口文档分析' },
  },
  {
    path: '/ui-automation',
    name: 'UiAutomationAgent',
    component: () => import('@/views/UiAutomationAgent.vue'),
    meta: { title: 'AI界面UI自动化脚本' },
  },
  {
    path: '/api-automation',
    name: 'ApiAutomationAgent',
    component: () => import('@/views/ApiAutomationAgent.vue'),
    meta: { title: 'AI接口自动化脚本助手' },
  },
  {
    path: '/performance-analysis',
    name: 'PerformanceAnalysisAssistant',
    component: () => import('@/views/PerformanceAnalysisAssistant.vue'),
    meta: { title: 'AI性能数据分析助手' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
