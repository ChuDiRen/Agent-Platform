<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getProject, type ProjectInfo } from '@/api/project'

defineOptions({ name: 'ProjectDetail' })

const route = useRoute()
const router = useRouter()
const project = ref<ProjectInfo | null>(null)
const loading = ref(true)

async function loadProject() {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('无效的项目 ID')
    router.push('/projects')
    return
  }
  try {
    project.value = await getProject(id)
  } catch {
    ElMessage.error('项目不存在或加载失败')
    router.push('/projects')
  } finally {
    loading.value = false
  }
}

onMounted(loadProject)
</script>

<template>
  <div class="detail-page">
    <!-- Top Navigation -->
    <header class="topbar animate-fade-in">
      <div class="topbar-left">
        <button class="back-btn" @click="router.push('/projects')">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
        <div class="logo">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="url(#logo-grad-d)" />
            <path
              d="M10 13L16 9L22 13V19L16 23L10 19V13Z"
              stroke="white"
              stroke-width="1.5"
              fill="none"
            />
            <circle cx="16" cy="16" r="2.5" fill="white" opacity="0.9" />
            <defs>
              <linearGradient id="logo-grad-d" x1="0" y1="0" x2="32" y2="32">
                <stop stop-color="#2563eb" />
                <stop offset="1" stop-color="#7c3aed" />
              </linearGradient>
            </defs>
          </svg>
          <span class="logo-text">{{ project?.name || '项目详情' }}</span>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="main-content">
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" :size="32"><i class="el-icon-loading" /></el-icon>
        <p>加载中...</p>
      </div>

      <template v-else-if="project">
        <!-- Project Header -->
        <section class="project-header animate-fade-up delay-1">
          <div class="header-info">
            <h1>{{ project.name }}</h1>
            <p class="desc">{{ project.description || '暂无描述' }}</p>
          </div>
        </section>

        <!-- Config Cards -->
        <section class="config-section animate-fade-up delay-2">
          <h2 class="section-title">模型配置</h2>
          <div class="config-grid">
            <!-- LLM Card -->
            <div class="config-card">
              <div class="config-card-header">
                <div class="config-icon llm-bg">
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <h3>LLM 语言模型</h3>
              </div>
              <div class="config-detail">
                <div class="config-item">
                  <span class="label">服务地址</span>
                  <span class="value">{{ project.llm_url || '未配置' }}</span>
                </div>
                <div class="config-item">
                  <span class="label">模型</span>
                  <span class="value">{{ project.llm_model || '未配置' }}</span>
                </div>
                <div class="config-item">
                  <span class="label">API Key</span>
                  <span class="value">{{ project.llm_key ? '••••••••' : '未配置' }}</span>
                </div>
              </div>
            </div>

            <!-- LVM Card -->
            <div class="config-card">
              <div class="config-card-header">
                <div class="config-icon lvm-bg">
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <circle cx="12" cy="12" r="4" />
                    <line x1="21.17" y1="8" x2="12" y2="8" />
                    <line x1="3.95" y1="6.06" x2="8.54" y2="14" />
                    <line x1="10.88" y1="21.94" x2="15.46" y2="14" />
                  </svg>
                </div>
                <h3>LVM 视觉模型</h3>
              </div>
              <div class="config-detail">
                <div class="config-item">
                  <span class="label">服务地址</span>
                  <span class="value">{{ project.lvm_url || '未配置' }}</span>
                </div>
                <div class="config-item">
                  <span class="label">模型</span>
                  <span class="value">{{ project.lvm_model || '未配置' }}</span>
                </div>
                <div class="config-item">
                  <span class="label">API Key</span>
                  <span class="value">{{ project.lvm_key ? '••••••••' : '未配置' }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Info Bar -->
        <section class="info-section animate-fade-up delay-3">
          <div class="info-card">
            <div class="info-item">
              <span class="info-label">项目 ID</span>
              <span class="info-value">#{{ project.id }}</span>
            </div>
            <div class="info-divider" />
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{
                project.created_at ? new Date(project.created_at).toLocaleString('zh-CN') : '-'
              }}</span>
            </div>
            <div class="info-divider" />
            <div class="info-item">
              <span class="info-label">更新时间</span>
              <span class="info-value">{{
                project.updated_at ? new Date(project.updated_at).toLocaleString('zh-CN') : '-'
              }}</span>
            </div>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped lang="scss">
.detail-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
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
  gap: 12px;
}

.back-btn {
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
    background: $color-bg-hover;
    color: $text-primary;
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;

  svg {
    width: 28px;
    height: 28px;
  }

  .logo-text {
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
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

.loading-state {
  @include flex-column-center;
  padding: 120px 0;
  gap: 12px;
  color: $text-secondary;
}

// --- Project Header ---
.project-header {
  margin-bottom: 40px;

  h1 {
    font-size: 28px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8px;
  }

  .desc {
    font-size: 15px;
    color: $text-secondary;
  }
}

// --- Config Section ---
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 20px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.config-card {
  padding: 24px;
  border-radius: $radius-lg;
  background: $color-bg-surface;
  border: 1px solid $border-color;
}

.config-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
  }
}

.config-icon {
  width: 36px;
  height: 36px;
  border-radius: $radius-md;
  @include flex-center;

  &.llm-bg {
    background: rgba($accent-primary, 0.08);
    color: $accent-primary;
  }

  &.lvm-bg {
    background: rgba($accent-secondary, 0.08);
    color: $accent-secondary;
  }
}

.config-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .label {
    font-size: 13px;
    color: $text-secondary;
  }

  .value {
    font-size: 13px;
    color: $text-primary;
    font-family: 'DM Sans', monospace;
    word-break: break-all;
    text-align: right;
    max-width: 60%;
  }
}

// --- Info Section ---
.config-section {
  margin-bottom: 40px;
}

.info-card {
  @include flex-between;
  padding: 20px 32px;
  border-radius: $radius-lg;
  background: $color-bg-surface;
  border: 1px solid $border-color;
  box-shadow: $shadow-sm;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: $text-secondary;
  letter-spacing: 0.05em;
}

.info-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.info-divider {
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

  .config-grid {
    grid-template-columns: 1fr;
  }

  .info-card {
    flex-wrap: wrap;
    gap: 16px;
    padding: 16px;
  }

  .info-divider {
    display: none;
  }

  .info-item {
    flex: 1;
    min-width: 120px;
  }
}
</style>
