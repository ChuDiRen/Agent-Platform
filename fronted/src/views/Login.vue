<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/store'
import { login } from '@/api/user'
import { ElMessage } from 'element-plus'

defineOptions({ name: 'Login' })

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

async function handleLogin() {
  if (!form.email || !form.password) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }

  loading.value = true
  try {
    const res = await login({ email: form.email, password: form.password })
    userStore.setToken(res.access_token)
    userStore.setUserInfo({
      userName: res.user.full_name || res.user.email,
      avatar: '',
      role: res.user.is_superuser ? 'admin' : 'user',
    })
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/home'
    router.push(redirect)
  } catch (error: any) {
    const detail = error?.response?.data?.detail
    if (detail === '邮箱或密码错误') {
      ElMessage.error('邮箱或密码错误，或账号已被禁用')
    } else {
      ElMessage.error(detail || '登录失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- Left: Brand Panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-icon animate-fade-up delay-1">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="48" height="48" rx="12" fill="url(#grad)" />
            <path d="M14 18L24 12L34 18V30L24 36L14 30V18Z" stroke="white" stroke-width="2" fill="none" />
            <circle cx="24" cy="24" r="4" fill="white" opacity="0.9" />
            <line x1="24" y1="20" x2="24" y2="12" stroke="white" stroke-width="1.5" opacity="0.6" />
            <line x1="24" y1="28" x2="24" y2="36" stroke="white" stroke-width="1.5" opacity="0.6" />
            <line x1="20.5" y1="22" x2="14" y2="18" stroke="white" stroke-width="1.5" opacity="0.6" />
            <line x1="27.5" y1="26" x2="34" y2="30" stroke="white" stroke-width="1.5" opacity="0.6" />
            <defs>
              <linearGradient id="grad" x1="0" y1="0" x2="48" y2="48">
                <stop stop-color="#2563eb" />
                <stop offset="1" stop-color="#7c3aed" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h1 class="brand-title animate-fade-up delay-2">Agent Platform</h1>
        <p class="brand-subtitle animate-fade-up delay-3">智能代理，无限可能</p>
        <div class="brand-features animate-fade-up delay-4">
          <div class="feature-item">
            <span class="feature-dot" />
            <span>多代理协同编排</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot" />
            <span>可视化工作流引擎</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot" />
            <span>实时监控与调试</span>
          </div>
        </div>
      </div>
      <div class="brand-decoration">
        <div class="deco-ring deco-ring--1" />
        <div class="deco-ring deco-ring--2" />
        <div class="deco-ring deco-ring--3" />
      </div>
    </div>

    <!-- Right: Form Panel -->
    <div class="form-panel">
      <div class="form-wrapper animate-fade-up delay-2">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>登录以继续使用 Agent Platform</p>
        </div>
        <el-form :model="form" @submit.prevent="handleLogin" class="login-form">
          <el-form-item>
            <el-input
              v-model="form.email"
              placeholder="邮箱地址"
              size="large"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              size="large"
              @click="handleLogin"
              class="login-btn"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="link">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
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
  background: linear-gradient(135deg, #eff6ff, #f5f3ff);

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

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: $text-regular;
  font-size: 14px;

  .feature-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: $accent-primary;
    box-shadow: 0 0 8px rgba(37, 99, 235, 0.3);
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
  border: 1px solid rgba(37, 99, 235, 0.06);

  &--1 {
    width: 500px;
    height: 500px;
    top: -100px;
    left: -100px;
    animation: orb-float 20s ease-in-out infinite;
  }
  &--2 {
    width: 300px;
    height: 300px;
    bottom: -50px;
    right: 100px;
    border-color: rgba(124, 58, 237, 0.06);
    animation: orb-float 25s ease-in-out infinite reverse;
  }
  &--3 {
    width: 200px;
    height: 200px;
    top: 40%;
    left: 30%;
    border-color: rgba(0, 0, 0, 0.03);
    animation: orb-float 18s ease-in-out infinite;
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

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
}

.login-btn {
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
    color: $accent-primary;
    font-weight: 500;
    margin-left: 4px;
    transition: color $transition-fast;

    &:hover {
      color: darken($accent-primary, 8%);
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
