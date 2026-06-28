# /comet-build 实施计划：平台安全与任务链路底座治理

change: secure-platform-foundation
build_mode: subagent-driven-development
isolation: branch
verify_mode: full

## 1. 构建目标

本阶段目标不是一次性重写平台，而是在现有架构上收紧五个底座边界：

```text
认证边界
  → 前端认证状态
    → 项目上下文
      → 运行配置
        → Agent Task 状态链路
```

每个边界都必须有对应回归证据，避免只完成代码表面迁移。

## 2. 执行方式

采用 `subagent-driven-development`，但不允许无约束并行。并行单元按模块边界拆分，最后由主流程统一集成和验证。

推荐节奏：

```text
阶段 A：影响面确认和接口分组
阶段 B：后端认证与配置边界
阶段 C：前端认证状态与项目上下文
阶段 D：Agent Task 状态链路对齐
阶段 E：全量验证与 Comet 状态推进
```

## 3. 子任务包

### 3.1 后端认证边界包

职责范围：

```text
backend/app/api/deps.py
backend/app/core/security.py
backend/app/api/v1/endpoints/*
tests/api/*auth* 或相关 API 测试
```

交付要求：

- 新增 `decode_access_token()`、`get_current_user()`、`get_current_active_user()`、`require_admin()`。
- 严格接受 `Authorization: Bearer <token>`。
- 公共接口保持匿名访问。
- 业务接口按粗粒度登录保护收口。
- 用户列表、用户删除等管理接口使用管理员依赖。
- 测试覆盖缺失 token、无效 token、过期 token、有效 token、普通用户访问管理员接口。

执行约束：

- 编辑任何已有函数前必须先做 GitNexus impact 分析。
- 不引入完整 RBAC 或项目成员体系。
- 不改变现有三层 CRUD 结构。

### 3.2 前端认证状态包

职责范围：

```text
fronted/src/api/http.ts
fronted/src/store/store.ts
fronted/src/utils/auth.ts
fronted/src/utils/permission.ts
tests/e2e/*
```

交付要求：

- 请求拦截器统一注入 `Authorization: Bearer <token>`。
- `401` 执行完整状态迁移：清 token、清持久化用户状态、跳转 `/login?redirect=...`。
- `403` 只提示无权限，不清理认证状态。
- 登录页和注册页避免循环跳转。
- E2E 覆盖登录失效行为。

执行约束：

- HTTP 层只调用 store 暴露的重置动作，不直接耦合 store 字段。
- redirect 必须保留 path 与 query。

### 3.3 项目上下文包

职责范围：

```text
fronted/src/composables/useProjectContext.ts
fronted/src/views/UiAutomationAgent.vue
fronted/src/views/ApiAutomationAgent.vue
fronted/src/views/*Agent*.vue
相关 E2E 或单元测试
```

交付要求：

- 新增统一项目上下文 helper。
- 从 `route.query.projectId` 读取并校验正整数项目 ID。
- 页面通过 helper 获取项目上下文，不再自行声明 `projectId = 1`。
- 至少迁移 `UiAutomationAgent.vue` 和 `ApiAutomationAgent.vue`。
- 搜索证明生产 Agent 页面不再硬编码 `projectId = 1`、`projectId: 1`、`project_id: 1`。

执行约束：

- 保留现有平铺路由，不做项目嵌套路由重构。
- 测试中的固定项目 ID 可以保留，但必须是测试数据语义。

### 3.4 运行配置边界包

职责范围：

```text
backend/app/core/config.py
tests/api/test_config.py
AGENTS.md / CLAUDE.md / backend 文档约定
```

交付要求：

- 配置优先级调整为：显式 init → 环境变量 → 代码默认值。
- 不强制启用 `.env` 文件。
- `DEBUG=false` 时拒绝危险默认值。
- 测试覆盖代码默认值、环境变量覆盖、生产危险默认值拒绝。
- 文档从“环境变量被禁用”改为“默认值在代码中，部署期可由环境变量覆盖”。

执行约束：

- 不新增 `.env` 或 `.env.example`。
- 不把真实密钥写入仓库。

### 3.5 Agent Task 状态链路包

职责范围：

```text
backend Agent Task endpoint / service / schema / model
fronted Agent Task store / adapter / task view
tests/api 与 tests/e2e 中任务相关测试
```

交付要求：

- 固化状态词汇：`pending`、`running`、`succeeded`、`failed`、`cancelled`、`retrying`。
- 后端 service 是状态迁移唯一裁决者。
- 前端只展示状态、发起 cancel / retry，不在页面私有推断复杂状态机。
- 认证保护后 create、poll、cancel、retry、events、artifacts 测试仍通过。

执行约束：

- 不重构 Celery / Redis / worker 架构。
- 不扩大为完整任务编排平台重写。

## 4. 集成检查点

### Checkpoint 1：后端边界可用

```text
公共接口匿名通过
受保护接口无 token 返回 401
有效 Bearer token 可访问受保护接口
普通用户访问管理员接口返回 403
```

### Checkpoint 2：前端认证状态闭环

```text
请求头格式为 Bearer token
401 后本地认证状态清空
401 后跳转登录页并保留 redirect
403 不清理 token
```

### Checkpoint 3：项目上下文不再硬编码

```text
Agent 页面通过 query projectId 获取上下文
生产代码不再出现 projectId = 1 类硬编码
项目级请求 payload 使用统一 helper 的项目 ID
```

### Checkpoint 4：配置可部署

```text
默认配置可用于本地开发
环境变量可覆盖默认值
生产模式拒绝危险默认值
```

### Checkpoint 5：任务状态可回归

```text
状态词汇前后端一致
任务 create / poll / cancel / retry / events / artifacts 链路通过认证保护后仍可用
```

## 5. 验证命令

按 full 验证执行：

```powershell
cd backend
.\venv\Scripts\pytest -v ..\tests\api
```

```powershell
cd fronted
pnpm build:prod
```

```powershell
npx playwright test
```

提交或进入 verify 前还需要执行 GitNexus 变更检测：

```text
detect_changes(repo: Agent-Platform)
```

## 6. 暂停与升级规则

需要暂停并回报的情况：

- GitNexus impact 返回 HIGH 或 CRITICAL。
- 认证保护导致公共接口或登录注册链路破坏。
- 项目上下文无法从现有路由稳定获得。
- 运行配置修改与现有测试约定冲突且无法局部迁移。
- Agent Task 后端状态词汇与数据库持久化值存在不兼容迁移风险。

## 7. 完成定义

- `openspec/changes/secure-platform-foundation/tasks.md` 所有任务被勾选。
- 所有 full 验证命令通过，或失败项有明确非本变更阻塞证据。
- GitNexus `detect_changes()` 影响范围符合本计划。
- `.comet.yaml` 可从 `build` 推进到 `verify`。