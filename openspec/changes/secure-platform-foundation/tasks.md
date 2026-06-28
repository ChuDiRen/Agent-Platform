# 任务清单

## 1. 认证与授权边界

- [x] 在 `backend/app/api/deps.py` 或独立认证依赖模块中增加 token 解码和当前用户依赖。
- [x] 增加 active user 和 admin user 依赖 helper。
- [x] 确定并记录 `Authorization` 请求头格式：严格使用 `Bearer <token>`，不兼容裸 token。
- [x] 对非公共业务 router 增加登录用户依赖。
- [x] 将用户管理变更接口、系统级 Agent 目录变更接口标记为管理员权限。
- [x] 增加 API 测试，覆盖缺失 token、无效 token、过期 token、有效 token。

## 2. 前端认证状态迁移

- [x] 更新 `fronted/src/api/http.ts`，让 `401` 清理 token 和持久化用户状态。
- [x] 认证失效时跳转到 `/login?redirect=<current-route>`，并避免登录页 / 注册页循环跳转。
- [x] 将 `403` 与 `401` 分开处理。
- [ ] 增加或更新登录过期行为的 E2E 覆盖。

## 3. 项目上下文正确性

- [x] 为项目级 Agent 页面引入统一项目上下文 helper。
- [x] 迁移 `UiAutomationAgent.vue`，移除 `projectId = 1`。
- [x] 迁移 `ApiAutomationAgent.vue`，移除 `projectId = 1`。
- [x] 搜索所有 Agent 页面和测试，证明生产页面不再硬编码 `projectId = 1`。
- [x] 增加项目级 Agent 导航和请求 payload 的回归覆盖。

## 4. 运行时配置边界

- [x] 修改 `Settings` 配置优先级：允许环境变量覆盖，同时保留代码默认值。
- [x] 更新当前断言“环境变量会被忽略”的配置测试。
- [x] 增加不安全生产默认值校验，重点覆盖 `SECRET_KEY`、CORS、Agent 模型凭据。
- [x] 更新项目指导文档，区分代码默认配置和部署期覆盖配置。

## 5. Agent Task 底座

- [x] 确认后端 Agent Task 状态和迁移规则是唯一标准。
- [ ] 让前端任务渲染和轮询逻辑对齐标准状态词汇。
- [x] 在认证保护下增加或更新 create、poll、cancel、retry、events、artifacts 测试。

## 6. 验证

- [x] 运行后端 API 测试：`cd backend && .\\venv\\Scripts\\pytest -v ..\\tests\\api`。
- [x] 运行前端构建：`cd fronted && pnpm build:prod`。
- [ ] 运行 E2E 测试：`npx playwright test` 或仓库配置的 E2E 命令。
- [ ] 提交或准备 PR 前运行 GitNexus `detect_changes()`。

## Build 验证证据

- `cd backend && .\\venv\\Scripts\\pytest -v ..\\tests\\api`：105 passed, 3 warnings。
- `cd fronted && pnpm build:prod`：通过，Vite production build 成功。
- `fronted/src/views/**/*.vue` 搜索 `projectId = 1|projectId: 1|project_id: 1`：无命中。
- `cd fronted && pnpm lint`：未进入源码检查，当前项目使用 ESLint 9.39.4，但仓库缺少 `eslint.config.*`，需单独迁移 ESLint 配置后再启用。
