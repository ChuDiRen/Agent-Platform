---
comet_change: secure-platform-foundation
role: technical-design
canonical_spec: openspec
---

# 平台安全与任务链路底座治理技术设计

## 1. 设计结论

本次变更采用“边界模块化路径”。目标不是做一次大规模平台重构，而是先补齐当前阻碍持续迭代的底座边界：认证、认证状态迁移、项目上下文、运行配置、Agent Task 状态模型。

核心数据流调整为：

```text
前端路由 / query projectId
  → useProjectContext()
    → 类型化 API 模块
      → HTTP 拦截器注入 Bearer token
        → 后端 current_user 依赖
          → endpoint / service / CRUD
            → 项目数据或 Agent Task 状态
```

本设计选择保留现有平铺路由，通过 `?projectId=...` 进行轻量兼容迁移。这样能解决 `projectId = 1` 的数据归属错误，同时避免在本变更中引入大规模路由和 Layout 重构。

## 2. 后端认证边界

### 2.1 模块职责

后端认证能力集中放在 `backend/app/api/deps.py` 或新建的认证依赖模块中。为了符合当前项目已有依赖注入风格，第一版建议仍放在 `deps.py`，后续如果文件膨胀再拆为 `api/auth.py`。

目标依赖结构：

```text
get_db()
  → 数据库会话生命周期

decode_access_token()
  → 校验 Authorization: Bearer <token>
  → 校验 JWT 签名、算法、过期时间、subject

get_current_user()
  → 使用 subject 查询用户
  → 用户不存在则返回 401

get_current_active_user()
  → 用户必须 is_active
  → 不启用返回 403

require_admin()
  → 用户必须 is_superuser
  → 非管理员返回 403
```

### 2.2 请求头策略

只接受标准格式：

```text
Authorization: Bearer <token>
```

不兼容裸 token。这样能避免前后端存在两套认证格式，也让后续接入标准 OAuth2 / OpenAPI 文档更自然。

### 2.3 接口保护范围

保持匿名访问：

```text
POST /api/v1/users/
POST /api/v1/users/login
GET /
GET /health
```

需要登录：

```text
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
```

管理员优先覆盖：

```text
GET /api/v1/users/
DELETE /api/v1/users/{user_id}
系统级 Agent 目录变更接口
```

本阶段不实现项目成员模型，因此暂不做“用户是否属于某项目”的细粒度权限。项目所有权 / 成员权限应作为后续独立 change 设计。

## 3. 前端认证状态边界

### 3.1 请求阶段

`fronted/src/api/http.ts` 的请求拦截器统一注入：

```text
Authorization: Bearer <token>
```

如果没有 token，不注入 Authorization。

### 3.2 响应阶段

`401` 是认证失效状态，必须触发完整状态迁移：

```text
收到 401
  → 结束 NProgress
  → 递减 loading
  → removeToken()
  → userStore.resetUser()
  → router.replace('/login?redirect=<current-route>')
```

`403` 表示已认证但无权限，只展示“没有权限访问”，不清理 token。

### 3.3 Store 设计

在用户 store 中增加显式 `resetUser()`，由 store 自己负责清理：

```text
resetUser()
  → token = ''
  → userName = ''
  → avatar = ''
  → role = ''
```

HTTP 层只调用 `resetUser()`，不直接知道 store 内部字段，避免状态结构变化时扩散修改。

### 3.4 跳转规则

- 当前在 `/login` 或 `/register` 时，不重复跳转。
- 其他页面跳转到 `/login?redirect=<current-route>`。
- redirect 应包含 path 和 query，避免项目上下文丢失。

## 4. 项目上下文边界

### 4.1 路由策略

采用轻量兼容策略：保留现有平铺路由，通过 query 传递项目上下文。

示例：

```text
/ui-automation?projectId=123
/api-automation?projectId=123
/test-data-generator?projectId=123
```

### 4.2 统一 helper

新增：

```text
fronted/src/composables/useProjectContext.ts
```

职责：

```text
读取 route.query.projectId
  → 转换为 number
  → 校验必须是正整数
  → 暴露 projectId / hasProjectContext / requireProjectId
  → 无效时提示并返回项目列表或项目详情入口
```

Agent 页面只消费 helper，不自己解析 route，也不定义 `projectId = 1`。

### 4.3 迁移范围

本变更至少迁移：

```text
fronted/src/views/UiAutomationAgent.vue
fronted/src/views/ApiAutomationAgent.vue
```

同时搜索所有 Agent 页面，确保生产代码不再出现硬编码：

```text
projectId = 1
projectId: 1
project_id: 1
```

测试文件可以保留固定项目 ID，但应明确是测试数据。

## 5. 运行时配置边界

### 5.1 配置优先级

`Settings` 应支持：

```text
显式 init settings
  → 环境变量
    → 代码默认值
```

不强制启用 `.env` 文件。项目仍然可以坚持“不提交 .env / 不依赖 .env”，但必须允许 CI、Docker、生产环境通过环境变量覆盖。

### 5.2 必须支持覆盖的配置

```text
PROJECT_NAME
DEBUG
DATABASE_URL
SECRET_KEY
BACKEND_CORS_ORIGINS
CELERY_BROKER_URL
CELERY_RESULT_BACKEND
CELERY_BROKER_CONNECTION_TIMEOUT
CELERY_TASK_ALWAYS_EAGER
AGENT_MODEL_SPEC
AGENT_MODEL_BASE_URL
AGENT_MODEL_API_KEY
```

### 5.3 生产安全校验

当 `DEBUG=false` 时，应拒绝明显不安全默认值：

```text
SECRET_KEY == 'change-me-in-production-please'
BACKEND_CORS_ORIGINS == ['*']
AGENT_MODEL_API_KEY 为空或默认占位值
```

该校验应通过 Pydantic validator 或启动前显式校验实现。测试需要覆盖安全默认值被拒绝的场景。

## 6. Agent Task 状态边界

本变更不重构 Celery、worker、Agent 执行器，只固化状态模型和测试约束。

标准状态词汇：

```text
pending
running
succeeded
failed
cancelled
retrying
```

建议迁移规则：

```text
pending → running
pending → cancelled
running → succeeded
running → failed
running → cancelled
failed → retrying → pending
```

后端 service 是状态迁移唯一裁决者。前端负责展示状态、发起 cancel / retry 请求，不在页面中推断复杂状态机。

事件和产物保持追加式：

```text
AgentTaskEvent: append-only
AgentArtifact: append-only from user perspective
```

## 7. 测试策略

### 7.1 后端测试

新增或调整测试覆盖：

```text
公共接口无需 token 可访问
受保护接口缺 token 返回 401
受保护接口无效 token 返回 401
受保护接口过期 token 返回 401
受保护接口有效 token 可访问
普通用户访问管理员接口返回 403
管理员访问管理员接口成功
```

配置测试从“环境变量被忽略”改为：

```text
代码默认值存在
环境变量可覆盖默认值
DEBUG=false 时危险默认值被拒绝
```

Agent Task 测试需要在认证保护后继续覆盖：

```text
create
poll
cancel
retry
events
artifacts
```

### 7.2 前端测试

E2E 或组件级测试覆盖：

```text
401 后清理 token 和 user_info
401 后跳转 /login?redirect=...
403 不清理 token
Agent 页面从 ?projectId 获取项目上下文
生产 Agent 页面不再硬编码 projectId = 1
```

已有 `tests/e2e` 和 `playwright.config.ts` 可以复用，不需要新建测试框架。

## 8. 实施顺序

1. 后端先补认证依赖和认证测试。
2. 后端分批保护 endpoint，更新共享测试 fixture。
3. 前端改 Bearer token 注入和 401 状态迁移。
4. 新增 `useProjectContext()`，迁移硬编码 projectId 页面。
5. 修改 `Settings` 优先级和配置测试。
6. 对齐 Agent Task 状态词汇和相关测试。
7. 运行后端测试、前端构建、E2E、GitNexus `detect_changes()`。

## 9. 风险与取舍

### 不做完整项目权限模型

当前没有项目成员模型。强行在本变更中加入 ownership / membership 会扩大数据库 schema、接口语义和前端页面范围。当前先解决认证和项目 ID 正确性，成员权限后续单独设计。

### 不做项目嵌套路由

嵌套路由更符合长期结构，但会影响导航、E2E、页面入口和可能的用户书签。本次选择 query 兼容策略，先修复数据归属错误。

### 不兼容裸 token

严格使用 Bearer 能减少迁移期分支逻辑，也更符合标准 HTTP 认证格式。代价是所有前端和测试 fixture 必须同步调整。

### 配置约定需要更新

当前项目文档写着“禁用环境变量”。这与部署安全冲突。本设计保留代码默认值，但允许环境变量覆盖，是对原约定的收敛而不是完全推翻。

## 10. 验收标准

- 后端受保护业务接口没有 token 时返回 `401`。
- 前端所有认证请求使用 `Authorization: Bearer <token>`。
- `401` 会清理 Cookie token 和 Pinia 持久化用户状态。
- `UiAutomationAgent.vue`、`ApiAutomationAgent.vue` 不再写死 `projectId = 1`。
- `Settings` 能被环境变量覆盖。
- 配置测试不再断言环境变量被忽略。
- Agent Task 相关测试在认证保护后仍能通过。
- `detect_changes()` 显示影响范围与本 change 一致。