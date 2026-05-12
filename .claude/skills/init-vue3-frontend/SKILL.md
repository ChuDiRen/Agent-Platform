---
name: init-vue3-frontend
description: 初始化 Vite + Vue 3 + TypeScript + Pinia 前端项目，包含 Element Plus、Axios、Vue Router、ESLint、Prettier 等完整工程化配置
user_invocable: true
---

# Vite + Vue 3 + TypeScript + Pinia 前端项目初始化

## 触发条件
用户要求创建/初始化 Vue 3 前端项目、前端脚手架、Vue+TS 项目模板时触发。

## 执行流程

### 阶段一：收集项目信息

向用户确认以下信息（如果未指定则使用默认值）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 项目名称 | `my-vue3-app` | 项目文件夹名 |
| 包管理器 | `pnpm` | pnpm / yarn / npm |
| UI 框架 | `element-plus` | element-plus / ant-design-vue / 不需要 |
| 是否需要 Pinia 持久化 | 是 | pinia-plugin-persistedstate |
| 端口号 | `3000` | 开发服务器端口 |
| 后端端口 | `8000` | 用于配置代理 |

### 阶段二：创建项目

```bash
# 使用 Vite 创建项目
pnpm create vite <项目名称> --template vue-ts
cd <项目名称>
pnpm install
```

### 阶段三：安装全部依赖

```bash
# 生产依赖
pnpm add vue-router pinia pinia-plugin-persistedstate element-plus @element-plus/icons-vue axios nprogress js-cookie

# 开发依赖
pnpm add -D @types/node @types/nprogress dart-sass sass terser \
  eslint eslint-plugin-vue @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  prettier eslint-config-prettier eslint-plugin-prettier \
  unplugin-auto-import unplugin-vue-components
```

### 阶段四：创建目录结构

```
src/
├── api/
│   ├── http.ts
│   ├── baseUrl.ts
│   └── modules/           # 按业务模块组织
├── assets/style/
│   ├── _variables.scss    # SCSS 变量和混入（全局自动导入）
│   ├── reset.scss
│   ├── global.scss
│   └── elementReset.scss
├── components/
│   └── index.ts
├── router/
│   └── index.ts
├── store/
│   └── store.ts
├── utils/
│   ├── auth.ts
│   ├── nprogress.ts
│   ├── permission.ts
│   └── getAssestsFile.ts
├── views/
│   ├── Home.vue
│   └── Login.vue
├── App.vue
└── main.ts
```

### 阶段五：写入配置文件和源码

按照以下顺序创建文件，每个文件内容见下方模板：

#### 5.1 `vite.config.ts`

```ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default ({ mode }: any) => {
  const env = loadEnv(mode, process.cwd())
  return defineConfig({
    base: './',
    plugins: [
      vue(),
      AutoImport({
        imports: ['vue', 'vue-router'],
        dts: 'src/auto-import.d.ts',
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/assets/style/_variables.scss" as *;`,
        },
      },
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: env.VITE_ENV === 'production' ? 'dist' : 'dist-test',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: false,
          drop_debugger: true,
        },
      },
    },
  })
}
```

#### 5.2 `tsconfig.app.json`（追加 paths 配置）

在 `compilerOptions` 中添加：
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

#### 5.3 环境变量文件

`.env.development`（开发环境使用 Vite 代理，URL 为空）:
```
VITE_ENV = development
VITE_APP_WEB_URL = ''
```

`.env.production`（生产环境填写真实 API 地址）:
```
VITE_ENV = production
VITE_APP_WEB_URL = 'https://your-api.com'
```

#### 5.4 `.eslintrc.cjs`

```js
module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
    'prettier',
  ],
  globals: {
    defineProps: 'readonly',
    defineEmits: 'readonly',
    defineExpose: 'readonly',
    withDefaults: 'readonly',
  },
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/ban-types': 'off',
    '@typescript-eslint/no-non-null-assertion': 'off',
    eqeqeq: ['warn', 'always'],
    curly: ['warn', 'all'],
    'no-var': 'warn',
    'prefer-const': 'warn',
    semi: ['warn', 'never'],
  },
}
```

#### 5.5 `.eslintignore`

```
node_modules
dist
*.d.ts
```

#### 5.6 `.prettierrc.cjs`

```js
module.exports = {
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  semi: false,
  singleQuote: true,
  trailingComma: 'all',
  bracketSpacing: true,
  arrowParens: 'always',
  overrides: [
    {
      files: '*.json',
      options: { printWidth: 200 },
    },
  ],
}
```

#### 5.7 `.prettierignore`

```
node_modules
dist
*.d.ts
```

#### 5.8 `src/main.ts`

```ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@/assets/style/reset.scss'
import '@/assets/style/global.scss'
import '@/assets/style/elementReset.scss'
import '@/utils/permission'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

#### 5.9 `src/router/index.ts`

```ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

#### 5.10 `src/store/store.ts`

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore(
  'user',
  () => {
    const token = ref('')
    const userName = ref('')
    const avatar = ref('')
    const role = ref('')

    function setToken(val: string) {
      token.value = val
    }

    function setUserInfo(info: { userName: string; avatar: string; role: string }) {
      userName.value = info.userName
      avatar.value = info.avatar
      role.value = info.role
    }

    function logout() {
      token.value = ''
      userName.value = ''
      avatar.value = ''
      role.value = ''
    }

    return { token, userName, avatar, role, setToken, setUserInfo, logout }
  },
  {
    persist: {
      key: 'user_info',
      storage: localStorage,
      paths: ['token', 'userName', 'avatar', 'role'],
    },
  },
)
```

#### 5.11 `src/api/http.ts`

```ts
import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'
import { baseUrl } from './baseUrl'

const service = axios.create({
  baseURL: baseUrl,
  timeout: 15000,
})

service.interceptors.request.use(
  (config) => {
    NProgress.start()
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = token
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    NProgress.done()
    if (response.status === 200) {
      return response.data
    }
    ElMessage.error(response.data?.message || '请求失败')
    return Promise.reject(new Error('请求失败'))
  },
  (error) => {
    NProgress.done()
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 可在此处清除 token 并跳转登录页
    } else {
      ElMessage.error(error.message || '网络异常')
    }
    return Promise.reject(error)
  },
)

export function get<T>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, { params, ...config }) as Promise<T>
}

export function post<T>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config) as Promise<T>
}

export function upload<T>(url: string, formData: FormData): Promise<T> {
  return service.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }) as Promise<T>
}

export function download(url: string, params?: object) {
  const iframe = document.createElement('iframe')
  iframe.src = `${baseUrl}${url}?${new URLSearchParams(params as Record<string, string>)}`
  iframe.style.display = 'none'
  document.body.appendChild(iframe)
  setTimeout(() => document.body.removeChild(iframe), 5000)
}

export default service
```

#### 5.12 `src/api/baseUrl.ts`

```ts
const env = import.meta.env.VITE_ENV

// 开发环境使用 Vite 代理，不需要完整 URL
// 生产环境使用环境变量配置的 URL
const baseUrlMap: Record<string, string> = {
  development: import.meta.env.VITE_APP_WEB_URL || '',
  production: import.meta.env.VITE_APP_WEB_URL || '',
}

export const baseUrl = baseUrlMap[env] ?? ''
```

#### 5.13 `src/utils/auth.ts`

```ts
import Cookies from 'js-cookie'

const TOKEN_KEY = 'vue3_token'

export function getToken(): string | undefined {
  return Cookies.get(TOKEN_KEY)
}

export function setToken(token: string): void {
  Cookies.set(TOKEN_KEY, token, { expires: 7 })
}

export function removeToken(): void {
  Cookies.remove(TOKEN_KEY)
}
```

#### 5.14 `src/utils/nprogress.ts`

```ts
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

export default NProgress
```

#### 5.15 `src/utils/permission.ts`

```ts
import router from '@/router'
import { getToken } from '@/utils/auth'
import NProgress from '@/utils/nprogress'

const whiteList = ['/login']

router.beforeEach((to, _from, next) => {
  NProgress.start()
  document.title = (to.meta.title as string) || 'Vue3 App'

  const token = getToken()
  if (token) {
    if (to.path === '/login') {
      next({ path: '/home' })
    } else {
      next()
    }
  } else {
    if (whiteList.includes(to.path)) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})
```

#### 5.16 `src/utils/getAssestsFile.ts`

```ts
export function getAssetsFile(url: string): string {
  return new URL(`../assets/${url}`, import.meta.url).href
}
```

#### 5.17 `src/assets/style/_variables.scss`

```scss
// 全局 SCSS 变量
$primary-color: #409eff;
$success-color: #67c23a;
$warning-color: #e6a23c;
$danger-color: #f56c6c;
$info-color: #909399;

$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$text-placeholder: #c0c4cc;

$border-color: #dcdfe6;
$background-color: #f5f7fa;

// 全局混入
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin ellipsis($lines: 1) {
  overflow: hidden;
  text-overflow: ellipsis;
  @if $lines == 1 {
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
  }
}
```

#### 5.18 `src/assets/style/reset.scss`

```scss
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

a {
  text-decoration: none;
  color: inherit;
}

ul, ol {
  list-style: none;
}

img {
  max-width: 100%;
  vertical-align: middle;
}

input, button, textarea {
  outline: none;
  border: none;
}
```

#### 5.19 `src/assets/style/global.scss`

```scss
@use 'variables' as *;

// 全局样式（如需添加）
```

#### 5.20 `src/assets/style/elementReset.scss`

```scss
// Element Plus 样式覆盖（按需自定义）
```

#### 5.21 `src/components/index.ts`

```ts
import type { App } from 'vue'

// 在此导入并注册全局公共组件
// import MyComponent from './MyComponent.vue'

export default {
  install(app: App) {
    // app.component('MyComponent', MyComponent)
  },
}
```

#### 5.22 `src/App.vue`

```vue
<script setup lang="ts">
</script>

<template>
  <router-view />
</template>

<style lang="scss">
#app {
  width: 100%;
  height: 100%;
}
</style>
```

#### 5.23 `src/views/Home.vue`

```vue
<script setup lang="ts">
defineOptions({ name: 'Home' })
</script>

<template>
  <div class="home-container">
    <h1>欢迎使用 Vue 3 + TypeScript + Pinia</h1>
    <p>项目已成功初始化</p>
    <el-button type="primary" @click="$router.push('/login')">前往登录</el-button>
  </div>
</template>

<style scoped lang="scss">
.home-container {
  @include flex-center;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}
</style>
```

#### 5.24 `src/views/Login.vue`

```vue
<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/store'

defineOptions({ name: 'Login' })

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: '',
})

function handleLogin() {
  // TODO: 对接实际登录接口
  userStore.setToken('mock_token')
  userStore.setUserInfo({
    userName: form.username,
    avatar: '',
    role: 'admin',
  })
  const redirect = (route.query.redirect as string) || '/home'
  router.push(redirect)
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>用户登录</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.login-container {
  @include flex-center;
  height: 100%;
  background: $background-color;

  .login-card {
    width: 420px;
    h2 {
      text-align: center;
      margin-bottom: 24px;
      color: $text-primary;
    }
  }
}
</style>
```

### 阶段六：更新 package.json scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build:dev": "vite build --mode development",
    "build:prod": "vite build --mode production",
    "lint": "eslint src --fix --ext .ts,.tsx,.vue,.js,.jsx",
    "prettier": "prettier --write ."
  }
}
```

### 阶段七：验证

```bash
# 启动开发服务器验证
pnpm dev
```

## 输出清单

完成后告知用户：
1. 项目已创建的目录结构
2. 已安装的依赖列表
3. 可用的脚本命令（`pnpm dev` / `pnpm build:prod` / `pnpm lint`）
4. 如需自定义可修改的配置文件位置
