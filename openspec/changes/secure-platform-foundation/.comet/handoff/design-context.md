# Comet Design Handoff

- Change: secure-platform-foundation
- Phase: design
- Mode: compact
- Context hash: 63c418080209c7156eea48f7b88c51a8f4d1e50ad891bf58f3cda73bb6f0cb6f

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/secure-platform-foundation/proposal.md

- Source: openspec/changes/secure-platform-foundation/proposal.md
- Lines: 1-67
- SHA256: ac4b324345e9058c5ce219bb19535a607e5bc9f24edc8ae0afa6096855bc8d14

```md
# 平台安全与任务链路底座治理

## 背景

Agent-Platform 已经从一个基础全栈模板演进为 AI Agent 测试平台。当前代码库已经具备项目管理、多个 Agent 工作台、Agent Task 任务中心、Celery/Redis 集成、Playwright E2E 测试以及后端 API 测试。

但平台级底座没有跟上业务能力扩张。基于最新 GitNexus 索引和当前文件检查，主要存在四类结构性缺口：

1. 后端登录接口会签发 JWT，但业务 API 没有一致地校验 token。
2. 前端收到 `401` 后只提示错误，没有把用户状态迁移回未登录状态。
3. 部分 Agent 页面仍然写死项目归属，例如 `projectId = 1`。
4. JWT 密钥、Redis 地址、CORS、模型服务配置等运行时敏感配置被固定在源码里，现有测试还在固化这种行为。

这些问题会导致访问边界不清晰、数据归属错误、部署困难，以及 Agent 任务链路后续演进脆弱。

## 目标

- 建立真实的后端认证与授权边界，让业务 API 必须经过身份校验。
- 让前端认证状态迁移变得明确：token 失效后能自动清理状态并回到登录页。
- 移除 Agent 页面中的硬编码项目归属，建立统一的项目上下文来源。
- 保留代码默认配置，但允许通过环境变量覆盖运行时敏感配置。
- 标准化 Agent Task 领域模型，使新增 Agent 页面能够复用状态、事件、产物、取消、重试等能力。
- 为上述关键链路补充回归测试。

## 范围

### 后端

- 增加 JWT 解码和当前用户依赖。
- 增加 active user 和 admin user 依赖边界。
- 对项目、Agent、文档、自动化、性能、测试数据、测试用例、Agent Task 等业务接口增加认证保护。
- 调整配置加载方式：保留代码默认值，但允许部署环境覆盖敏感和运行时配置。
- 更新配置测试，使其验证新的配置优先级。
- 增加或调整 API 测试，覆盖受保护路由、过期 token、无效 token、管理员权限等场景。

### 前端

- 更新 HTTP 层对 `401` 和 `403` 的处理。
- 认证失败时清理 Cookie token 和持久化用户状态。
- 自动跳转到 `/login`，并保留原目标路由。
- 为项目级 Agent 页面引入统一项目上下文。
- 移除已知的 `projectId = 1` 硬编码。
- 增加 E2E 或 API 级测试，覆盖登录失效和项目级 Agent 导航。

### Agent Task 底座

- 明确 Agent Task 的标准状态模型。
- 确保前后端使用一致的任务状态词汇。
- 扩展 create、poll、cancel、retry、events、artifacts 等链路测试。

## 非目标

- 不在本变更中实现完整多租户 RBAC 或项目成员体系。
- 不迁移 SQLite 到其他数据库。
- 不重写所有 Agent 页面 UI。
- 不替换 Celery/Redis 或重构整个 Agent 执行架构。
- 不解决所有样式和 Layout 重复问题。
- 不强制引入 `.env` 文件；本变更只要求具备运行时覆盖能力。

## 成功标准

- 业务 API 能拒绝缺失、无效、过期的认证凭据。
- 登录、注册、根路径、健康检查等公共接口仍可匿名访问。
- 前端在请求返回 `401` 时能自动清理认证状态并跳转登录页。
- Agent 页面从路由或统一上下文获取项目归属，不再依赖固定常量。
- 配置可以通过环境变量覆盖，便于测试、CI 和部署。
- 现有后端 API 测试和前端 E2E 测试在更新后通过。
- 新增回归测试覆盖认证边界、配置优先级，以及至少一个项目级 Agent 流程。```

## openspec/changes/secure-platform-foundation/design.md

- Source: openspec/changes/secure-platform-foundation/design.md
- Lines: 1-270
- SHA256: b6b73d089a83ab8ed45f2c4c3a5cbac4a1ce86707ff9de824de5947a5fb844da

[TRUNCATED]

```md
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

```

Full source: openspec/changes/secure-platform-foundation/design.md

## openspec/changes/secure-platform-foundation/tasks.md

- Source: openspec/changes/secure-platform-foundation/tasks.md
- Lines: 1-44
- SHA256: a135f1340229f4138479ded5d349eb59932081998096df5068db8e0909a7614a

```md
# 任务清单

## 1. 认证与授权边界

- [ ] 在 `backend/app/api/deps.py` 或独立认证依赖模块中增加 token 解码和当前用户依赖。
- [ ] 增加 active user 和 admin user 依赖 helper。
- [ ] 确定并记录 `Authorization` 请求头格式，建议使用 `Bearer <token>`，迁移期可临时兼容裸 token。
- [ ] 对非公共业务 router 增加登录用户依赖。
- [ ] 将用户管理变更接口、系统级 Agent 目录变更接口标记为管理员权限。
- [ ] 增加 API 测试，覆盖缺失 token、无效 token、过期 token、有效 token。

## 2. 前端认证状态迁移

- [ ] 更新 `fronted/src/api/http.ts`，让 `401` 清理 token 和持久化用户状态。
- [ ] 认证失效时跳转到 `/login?redirect=<current-route>`，并避免登录页 / 注册页循环跳转。
- [ ] 将 `403` 与 `401` 分开处理。
- [ ] 增加或更新登录过期行为的 E2E 覆盖。

## 3. 项目上下文正确性

- [ ] 为项目级 Agent 页面引入统一项目上下文 helper。
- [ ] 迁移 `UiAutomationAgent.vue`，移除 `projectId = 1`。
- [ ] 迁移 `ApiAutomationAgent.vue`，移除 `projectId = 1`。
- [ ] 搜索所有 Agent 页面和测试，证明生产页面不再硬编码 `projectId = 1`。
- [ ] 增加项目级 Agent 导航和请求 payload 的回归覆盖。

## 4. 运行时配置边界

- [ ] 修改 `Settings` 配置优先级：允许环境变量覆盖，同时保留代码默认值。
- [ ] 更新当前断言“环境变量会被忽略”的配置测试。
- [ ] 增加不安全生产默认值校验，重点覆盖 `SECRET_KEY`、CORS、Agent 模型凭据。
- [ ] 更新项目指导文档，区分代码默认配置和部署期覆盖配置。

## 5. Agent Task 底座

- [ ] 确认后端 Agent Task 状态和迁移规则是唯一标准。
- [ ] 让前端任务渲染和轮询逻辑对齐标准状态词汇。
- [ ] 在认证保护下增加或更新 create、poll、cancel、retry、events、artifacts 测试。

## 6. 验证

- [ ] 运行后端 API 测试：`cd backend && .\\venv\\Scripts\\pytest -v ..\\tests\\api`。
- [ ] 运行前端构建：`cd fronted && pnpm build:prod`。
- [ ] 运行 E2E 测试：`npx playwright test` 或仓库配置的 E2E 命令。
- [ ] 提交或准备 PR 前运行 GitNexus `detect_changes()`。```

