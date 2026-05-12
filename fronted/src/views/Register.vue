<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { post } from '@/api/http'

defineOptions({ name: 'Register' })

const router = useRouter()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
  confirmPassword: '',
  full_name: '',
})

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

async function handleRegister() {
  if (!form.email || !form.password || !form.confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (!emailRegex.test(form.email)) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.warning('两次密码不一致')
    return
  }

  loading.value = true
  try {
    await post('/api/v1/users/', {
      email: form.email,
      password: form.password,
      full_name: form.full_name,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <!-- Left: Brand Panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-icon animate-fade-up delay-1">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="48" height="48" rx="12" fill="url(#grad-reg)" />
            <path d="M14 18L24 12L34 18V30L24 36L14 30V18Z" stroke="white" stroke-width="2" fill="none" />
            <circle cx="24" cy="24" r="4" fill="white" opacity="0.9" />
            <line x1="24" y1="20" x2="24" y2="12" stroke="white" stroke-width="1.5" opacity="0.6" />
            <line x1="24" y1="28" x2="24" y2="36" stroke="white" stroke-width="1.5" opacity="0.6" />
            <line x1="20.5" y1="22" x2="14" y2="18" stroke="white" stroke-width="1.5" opacity="0.6" />
            <line x1="27.5" y1="26" x2="34" y2="30" stroke="white" stroke-width="1.5" opacity="0.6" />
            <defs>
              <linearGradient id="grad-reg" x1="0" y1="0" x2="48" y2="48">
                <stop stop-color="#7c3aed" />
                <stop offset="1" stop-color="#2563eb" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h1 class="brand-title animate-fade-up delay-2">Agent Platform</h1>
        <p class="brand-subtitle animate-fade-up delay-3">加入我们，开启智能之旅</p>
        <div class="brand-stats animate-fade-up delay-4">
          <div class="stat-item">
            <span class="stat-value">10K+</span>
            <span class="stat-label">活跃用户</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">500+</span>
            <span class="stat-label">代理模板</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">99.9%</span>
            <span class="stat-label">可用性</span>
          </div>
        </div>
      </div>
      <div class="brand-decoration">
        <div class="deco-ring deco-ring--1" />
        <div class="deco-ring deco-ring--2" />
      </div>
    </div>

    <!-- Right: Form Panel -->
    <div class="form-panel">
      <div class="form-wrapper animate-fade-up delay-2">
        <div class="form-header">
          <h2>创建账号</h2>
          <p>注册以开始使用 Agent Platform</p>
        </div>
        <el-form :model="form" @submit.prevent="handleRegister" class="register-form">
          <el-form-item>
            <el-input
              v-model="form.email"
              placeholder="邮箱地址"
              size="large"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.full_name"
              placeholder="姓名（可选）"
              size="large"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="设置密码"
              size="large"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              size="large"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              size="large"
              @click="handleRegister"
              class="register-btn"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="link">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
}

// --- Brand Panel ---
.brand-panel {
  flex: 1;
  @include flex-column-center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f3ff, #eff6ff);

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to right, transparent 70%, $color-bg-deep);
    z-index: 1;
  }
}

.brand-content {
  position: relative;
  z-index: 2;
  padding: 60px;
}

.brand-icon {
  margin-bottom: 32px;
  svg {
    width: 64px;
    height: 64px;
  }
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 12px;
}

.brand-subtitle {
  font-size: 16px;
  color: $text-secondary;
  margin-bottom: 48px;
  letter-spacing: 0.1em;
}

.brand-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .stat-value {
    font-family: 'Sora', sans-serif;
    font-size: 24px;
    font-weight: 700;
    background: $accent-gradient;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .stat-label {
    font-size: 12px;
    color: $text-secondary;
    letter-spacing: 0.05em;
  }
}

.brand-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.deco-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(124, 58, 237, 0.06);

  &--1 {
    width: 400px;
    height: 400px;
    top: -80px;
    right: -80px;
    animation: orb-float 22s ease-in-out infinite;
  }
  &--2 {
    width: 250px;
    height: 250px;
    bottom: 10%;
    left: 20%;
    border-color: rgba(37, 99, 235, 0.05);
    animation: orb-float 18s ease-in-out infinite reverse;
  }
}

// --- Form Panel ---
.form-panel {
  width: 480px;
  @include flex-center;
  position: relative;
  z-index: 2;
  background: $color-bg-surface;
}

.form-wrapper {
  width: 360px;
}

.form-header {
  margin-bottom: 40px;

  h2 {
    font-size: 28px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: $text-secondary;
  }
}

.register-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
}

.register-btn {
  width: 100%;
  height: 44px !important;
  font-size: 15px !important;
  margin-top: 4px;
}

.form-footer {
  text-align: center;
  margin-top: 32px;
  font-size: 14px;
  color: $text-secondary;

  .link {
    color: $accent-secondary;
    font-weight: 500;
    margin-left: 4px;
    transition: color $transition-fast;

    &:hover {
      color: darken($accent-secondary, 8%);
    }
  }
}

// --- Responsive ---
@media (max-width: 768px) {
  .brand-panel {
    display: none;
  }
  .form-panel {
    width: 100%;
  }
}
</style>
