# 平台安全与任务链路底座治理设计

## 设计原则

本变更的核心目标不是到处增加临时判断，而是把平台边界收紧，并让边界职责清晰。

目标架构如下：

```text
前端路由 / 项目上下文
  → 类型化 API 模块
    → 具备认证状态迁移的 HTTP 拦截器
      → 后端认证依赖
        → 用户 / 项目范围内的 service 或 CRUD 层
          → 持久化任务和领域状态
```

边界定义：

- HTTP token 传输不等于用户身份。
- 用户身份不等于业务授权。
- 项目上下文不应该是页面内部常量。
- Agent 任务状态不应该是页面轮询逻辑的私有细节。
- 部署配置不应该固定在源码里。

## 后端认证边界

### 当前问题

后端可以签发 JWT，但 `app/api/deps.py` 没有提供当前用户依赖。大部分 endpoint 只依赖 `get_db()`，所以携带 token 和不携带 token 的请求在多数业务接口上没有本质区别。

### 目标依赖模型

```text
get_db()

decode_access_token()
  → 校验签名、算法、过期时间、subject

get_current_user()
  → token → 用户记录

get_current_active_user()
  → 当前用户必须启用

require_admin()
  → 当前启用用户必须是超级管理员
```

接口分类：

```text
公共接口：
  POST /users/
  POST /users/login
  GET /
  GET /health 或 /health/live

需要登录的业务接口：
  projects
  agents
  test-data
  test-cases
  documents
  api-documents
  api-automation
  ui-automation
  performance
  agent-tasks

候选管理员接口：
  用户列表
  用户删除
  系统级 Agent 目录变更
```

第一阶段应优先做粗粒度保护，不要在没有项目成员模型的情况下强行设计复杂 RBAC。

## 前端认证状态机

### 当前问题

`src/api/http.ts` 收到 `401` 时只显示“登录已过期”，但不会清理 Cookie token、Pinia 持久化状态，也不会跳转登录页。

### 目标状态迁移

```text
请求返回 401
  → 停止 loading / 进度条
  → 显示一次清晰的登录过期提示
  → 删除 token cookie
  → 重置用户 store
  → 跳转 /login?redirect=<current-route>
```

规则：

- 如果当前已经在 `/login` 或 `/register`，不能造成跳转循环。
- 保留原目标路由，便于重新登录后返回。
- `403` 与 `401` 分开处理：`401` 是未认证或认证失效，`403` 是已认证但无权限。

## 项目上下文边界

### 当前问题

部分 Agent 页面定义了 `projectId = 1` 这类局部常量。这样会造成 UI 显示的项目与 API 实际写入项目不一致。

### 目标模型

```text
/projects/:id
  → ProjectDetail
    → 进入项目级 Agent 页面时携带 projectId

Agent 页面
  → useProjectContext()
    → 从 route param / query 获取并校验 projectId
    → 必要时从选中项目 store 回退
    → 为 API payload 提供类型明确的 projectId
```

建议的最终路由结构：

```text
/projects/:id/agent-hub
/projects/:id/test-data-generator
/projects/:id/ai-test-cases
/projects/:id/requirement-review
/projects/:id/interface-document-analysis
/projects/:id/ui-automation
/projects/:id/api-automation
/projects/:id/performance-analysis
```

轻量第一步可以保留现有平铺路由，并兼容 `?projectId=...`。但最终更合理的结构是项目嵌套路由，因为这些页面本质上都是项目级能力。

## 配置边界

### 当前问题

`Settings.settings_customise_sources()` 只返回 `init_settings`，现有测试也断言环境变量会被忽略。这使得密钥和运行时配置只能写在源码里，不利于安全部署和 CI。

### 目标优先级

```text
显式 init settings
  → 环境变量
    → 代码默认值
```

如果项目约定不使用 `.env` 文件，可以继续禁用 `.env`；但必须允许环境变量覆盖，因为这是部署和 CI 的基本能力。

需要支持覆盖的配置：

```text
SECRET_KEY
BACKEND_CORS_ORIGINS
DATABASE_URL
CELERY_BROKER_URL
CELERY_RESULT_BACKEND
AGENT_MODEL_SPEC
AGENT_MODEL_BASE_URL
AGENT_MODEL_API_KEY
DEBUG
```

生产安全校验：

```text
如果 DEBUG 为 false：
  SECRET_KEY 不能是默认占位值
  如果启用 Agent 执行，AGENT_MODEL_API_KEY 不能为空或默认值
  CORS 不能是 ["*"]
```

## Agent Task 底座

### 当前状态

GitNexus 显示 Agent Task 已经是核心跨模块链路：

```text
create_agent_task → create_and_enqueue_agent_task → AgentTaskService.create_task
create_api_automation_exec → create_task
create_ui_automation_exec → create_task
analyze_document → create_task
review_document → create_task
analyze_performance_record → create_task
```

### 目标状态词汇

```text
pending
running
succeeded
failed
cancelled
retrying
```

后端应负责合法状态迁移。前端只渲染状态，不推断后端工作流规则。

建议状态迁移：

```text
pending → running
pending → cancelled
running → succeeded
running → failed
running → cancelled
failed → retrying → pending
```

从用户视角看，事件和产物应保持追加式记录，不应被前端覆盖或重写。

## 测试策略

### 后端

- 认证测试：
  - 公共接口仍可匿名访问。
  - 受保护接口拒绝缺失 token。
  - 受保护接口拒绝无效 token。
  - 受保护接口拒绝过期 token。
  - 受保护接口接受有效 token。
- 管理员测试：
  - 普通用户不能访问管理员接口。
  - 管理员可以访问管理员接口。
- 配置测试：
  - 环境变量可以覆盖代码默认值。
  - 不安全生产配置会被校验失败或拒绝启动。
- Agent Task 测试：
  - 增加认证后，create / poll / cancel / retry 链路仍然兼容。

### 前端

- 单测或 E2E 覆盖：
  - `401` 会清理认证状态并跳转。
  - 已登录用户访问登录页会跳转到项目页。
  - 项目级 Agent 导航会把 projectId 传入页面和请求。
  - 生产 Agent 页面不再出现 `projectId = 1`。

## 推进顺序

1. 先增加后端认证依赖和测试。
2. 分批保护 endpoint，并修复测试。
3. 更新前端 `401` 处理。
4. 引入项目上下文 helper，迁移硬编码 Agent 页面。
5. 更新配置优先级和相关测试。
6. 补齐 Agent Task 状态与测试覆盖。

这个顺序可以降低风险：先稳定后端契约，再让前端依赖新契约。

## 风险与应对

### 风险：增加认证后打破现有测试和 E2E setup

应对：更新共享测试 fixture，统一创建用户、登录并传入 `Authorization`。

### 风险：当前前端发送的是裸 token，而不是 `Bearer <token>`

应对：确定统一格式。建议采用 `Authorization: Bearer <token>`，迁移期后端可以临时兼容裸 token。

### 风险：当前没有项目成员模型

应对：本阶段先做认证和项目 ID 正确性；项目所有权 / 成员权限作为后续独立变更。

### 风险：环境变量覆盖与现有“配置写在代码里”的约定冲突

应对：保留代码默认值，不强制 `.env` 文件，但允许环境变量覆盖。文档中明确区分“本地默认配置”和“部署期运行配置”。