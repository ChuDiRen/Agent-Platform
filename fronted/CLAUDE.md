# Frontend — CLAUDE.md

Vue 3 单页应用，Agent Platform 前端。

## 技术栈

Vue 3 + TypeScript + Vite 6 + Pinia + Element Plus + SCSS

## 目录结构

```
src/
├── main.ts              # 入口：Pinia + Router + Element Plus + 权限守卫
├── App.vue              # 根组件（背景网格 + 渐变光球 + router-view）
├── views/
│   ├── Login.vue        # 登录页（左右分栏：品牌 + 表单）
│   ├── Register.vue     # 注册页（同上布局）
│   └── Home.vue         # 首页仪表盘（导航栏 + 快捷操作 + 状态栏）
├── router/index.ts      # 路由：/ → /home, /login, /register（懒加载）
├── store/store.ts       # Pinia 用户状态（持久化到 localStorage）
├── api/
│   ├── http.ts          # Axios 封装（拦截器 + NProgress + 错误处理）
│   ├── baseUrl.ts       # API Base URL 代码常量
│   └── user.ts          # 用户 API（login / getUserInfo / getUsers）
├── utils/
│   ├── auth.ts          # Cookie token 管理（js-cookie，key: vue3_token）
│   ├── permission.ts    # 路由守卫（白名单：/login, /register）
│   └── nprogress.ts     # NProgress 配置
├── components/index.ts  # 全局组件注册（当前为空）
└── assets/style/
    ├── _variables.scss  # 设计 token + mixin（全局注入）
    ├── reset.scss       # CSS reset + 字体（Sora / DM Sans / JetBrains Mono）
    ├── global.scss      # 背景效果 + 动画工具类
    └── elementReset.scss # Element Plus 主题覆盖
```

## 核心模式

**自动导入**：
- Vue / Vue Router API 通过 `unplugin-auto-import` 全局导入，组件中无需显式 import
- Element Plus 组件通过 `unplugin-vue-components` 按需解析

**样式系统**：
- `_variables.scss` 通过 Vite `additionalData` 注入所有 SCSS 上下文
- 组件直接使用 `$变量` 和 `@include mixin`，无需 `@use`
- 设计 token：颜色、间距、圆角、阴影、过渡时间

**认证流程**：
- 登录：`POST /api/v1/users/login` → Pinia store + Cookie
- 守卫：`permission.ts` 的 `beforeEach` 检查 Cookie token
- 双重存储：Cookie（HTTP 拦截器读取）+ localStorage（UI 组件读取）

**页面布局**：
- 认证页（Login / Register）：左侧品牌面板 + 右侧表单面板，移动端隐藏品牌面板
- 首页（Home）：顶部导航 + 主内容区（欢迎 + 快捷操作 + 状态栏）

## 路由

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | — | 重定向到 `/home` |
| `/home` | Home.vue | 首页仪表盘（需认证） |
| `/login` | Login.vue | 登录页 |
| `/register` | Register.vue | 注册页 |

## 开发命令

```powershell
cd fronted
pnpm install           # 安装依赖
pnpm dev               # 开发服务器 → http://localhost:3000
pnpm build:prod        # 生产构建
pnpm lint              # ESLint 修复
pnpm prettier          # 代码格式化
```

E2E 测试：
```powershell
npm run test:e2e           # 运行所有测试
npm run test:e2e:headed    # 有头模式
npm run test:e2e:ui        # UI 模式
npm run test:e2e:debug     # 调试模式
npm run test:e2e:report    # 查看报告
```

## 前后端联调

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- Vite 代理：`/api/*` → `http://localhost:8000`
- 前端不使用 `.env*` 文件；API Base URL 和代理目标写在代码配置中

## E2E 测试

- 配置：`playwright.config.ts`
- 测试目录：`tests/e2e/`
- 认证 setup：`auth.setup.ts` mock 登录 API 并保存 storage state
- 测试文件：`login.spec.ts`、`register.spec.ts`、`home.spec.ts`、`navigation.spec.ts`
- 所有 API 调用通过 `page.route()` mock，无需后端运行

## 约定

- 组件使用 `<script setup lang="ts">` + `defineOptions({ name: '...' })`
- 路径别名：`@` → `src/`
- 包管理器：pnpm
- 端口：3000（开发）
- 中文 UI：所有用户可见文本为中文
- Element Plus 表单使用 `placeholder` 定位（无 `<label>`）
