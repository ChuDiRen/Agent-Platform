<script setup lang="ts">
import { useUserStore } from '@/store/store'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

defineOptions({ name: 'Home' })

const userStore = useUserStore()
const router = useRouter()

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const quickActions = [
  { label: '创建代理', desc: '从零开始构建智能代理', color: '#2563eb' },
  { label: '工作流', desc: '设计多代理协同流程', color: '#7c3aed' },
  { label: '模板库', desc: '使用预置模板快速开始', color: '#f59e0b' },
  { label: '数据源', desc: '连接外部数据与服务', color: '#10b981' },
]
</script>

<template>
  <div class="home-page">
    <!-- Top Navigation -->
    <header class="topbar animate-fade-in">
      <div class="topbar-left">
        <div class="logo">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="url(#logo-grad)" />
            <path d="M10 13L16 9L22 13V19L16 23L10 19V13Z" stroke="white" stroke-width="1.5" fill="none" />
            <circle cx="16" cy="16" r="2.5" fill="white" opacity="0.9" />
            <defs>
              <linearGradient id="logo-grad" x1="0" y1="0" x2="32" y2="32">
                <stop stop-color="#2563eb" />
                <stop offset="1" stop-color="#7c3aed" />
              </linearGradient>
            </defs>
          </svg>
          <span class="logo-text">Agent Platform</span>
        </div>
      </div>
      <div class="topbar-right">
        <div class="user-badge">
          <div class="avatar">{{ (userStore.userName || 'U')[0].toUpperCase() }}</div>
          <span class="user-name">{{ userStore.userName }}</span>
          <span class="role-tag" v-if="userStore.role === 'admin'">Admin</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Welcome Section -->
      <section class="welcome-section animate-fade-up delay-1">
        <div class="welcome-text">
          <h1>
            你好，<span class="highlight">{{ userStore.userName || '用户' }}</span>
          </h1>
          <p>欢迎回到 Agent Platform，今天想创建什么？</p>
        </div>
      </section>

      <!-- Quick Actions -->
      <section class="actions-section animate-fade-up delay-3">
        <h2 class="section-title">快速开始</h2>
        <div class="actions-grid">
          <div
            v-for="(action, i) in quickActions"
            :key="i"
            class="action-card"
          >
            <div class="action-icon" :style="{ background: `${action.color}10`, color: action.color }">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="16" />
                <line x1="8" y1="12" x2="16" y2="12" />
              </svg>
            </div>
            <div class="action-info">
              <h3>{{ action.label }}</h3>
              <p>{{ action.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Status Bar -->
      <section class="status-section animate-fade-up delay-4">
        <div class="status-card">
          <div class="status-item">
            <span class="status-label">系统状态</span>
            <span class="status-value online">运行中</span>
          </div>
          <div class="status-divider" />
          <div class="status-item">
            <span class="status-label">活跃代理</span>
            <span class="status-value">0</span>
          </div>
          <div class="status-divider" />
          <div class="status-item">
            <span class="status-label">今日任务</span>
            <span class="status-value">0</span>
          </div>
          <div class="status-divider" />
          <div class="status-item">
            <span class="status-label">角色</span>
            <span class="status-value">{{ userStore.role === 'admin' ? '管理员' : '普通用户' }}</span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped lang="scss">
.home-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

// --- Top Bar ---
.topbar {
  @include flex-between;
  padding: 0 $spacing-xl;
  height: 64px;
  border-bottom: 1px solid $border-color;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;

  svg {
    width: 32px;
    height: 32px;
  }

  .logo-text {
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: $accent-gradient;
  @include flex-center;
  font-family: 'Sora', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.user-name {
  font-size: 14px;
  color: $text-regular;
  font-weight: 500;
}

.role-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: $radius-full;
  background: rgba($accent-secondary, 0.08);
  color: $accent-secondary;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.logout-btn {
  @include flex-center;
  width: 36px;
  height: 36px;
  border-radius: $radius-md;
  background: transparent;
  border: 1px solid $border-color;
  color: $text-secondary;
  cursor: pointer;
  transition: all $transition-base;

  &:hover {
    background: rgba($danger-color, 0.06);
    border-color: rgba($danger-color, 0.3);
    color: $danger-color;
  }
}

// --- Main Content ---
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-2xl $spacing-xl;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

// --- Welcome ---
.welcome-section {
  margin-bottom: 48px;
}

.welcome-text {
  h1 {
    font-size: 32px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8px;

    .highlight {
      background: $accent-gradient;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  p {
    font-size: 16px;
    color: $text-secondary;
  }
}

// --- Actions ---
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.action-card {
  @include flex-between;
  gap: 16px;
  padding: 20px;
  border-radius: $radius-lg;
  background: $color-bg-surface;
  border: 1px solid $border-color;
  cursor: pointer;
  transition: all $transition-base;

  &:hover {
    border-color: rgba(37, 99, 235, 0.15);
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: $radius-md;
  @include flex-center;
  flex-shrink: 0;
}

.action-info {
  flex: 1;

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 4px;
  }

  p {
    font-size: 13px;
    color: $text-secondary;
  }
}

// --- Status ---
.status-section {
  margin-top: 48px;
}

.status-card {
  @include flex-between;
  padding: 20px 32px;
  border-radius: $radius-lg;
  background: $color-bg-surface;
  border: 1px solid $border-color;
  box-shadow: $shadow-sm;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-label {
  font-size: 12px;
  color: $text-secondary;
  letter-spacing: 0.05em;
}

.status-value {
  font-family: 'Sora', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;

  &.online {
    color: $success-color;
    &::before {
      content: '';
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: $success-color;
      margin-right: 6px;
      box-shadow: 0 0 6px rgba($success-color, 0.4);
    }
  }
}

.status-divider {
  width: 1px;
  height: 36px;
  background: $border-color;
}

// --- Responsive ---
@media (max-width: 768px) {
  .topbar {
    padding: 0 $spacing-md;
  }

  .main-content {
    padding: $spacing-lg $spacing-md;
  }

  .welcome-text h1 {
    font-size: 24px;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .status-card {
    flex-wrap: wrap;
    gap: 16px;
    padding: 16px;
  }

  .status-divider {
    display: none;
  }

  .status-item {
    flex: 1;
    min-width: 120px;
  }
}
</style>
