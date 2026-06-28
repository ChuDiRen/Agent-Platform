# AGENTS.md

本文件为 Codex (Codex.ai/code) 在此仓库中工作时提供指导。

## 项目概述

Agent-Platform 是一个全栈 monorepo，前后端分离。采用 Apache 2.0 许可证。

## 架构

```
Agent-Platform/
├── fronted/          # Vue 3 单页应用（注意：目录名拼写为 "fronted"）
├── backend/          # FastAPI REST API
├── start.ps1         # 一键启动（自动清理端口占用）
├── stop.ps1          # 一键停止
└── .Codex/skills/   # Codex 项目技能
```

> 各子项目详细文档见 [fronted/AGENTS.md](fronted/AGENTS.md) 和 [backend/AGENTS.md](backend/AGENTS.md)。

### 前端 (`fronted/`)

- **技术栈**: Vue 3 + TypeScript + Vite 6 + Pinia + Element Plus
- **设计主题**: 白色风格，Sora + DM Sans 字体，蓝紫渐变主色 (#2563eb → #7c3aed)
- **状态管理**: Pinia + `pinia-plugin-persistedstate`（localStorage 持久化，key: `user_info`）
- **HTTP**: Axios，拦截器自动注入 Cookie token，NProgress 进度条
- **路由**: Vue Router history 模式，登录守卫白名单: `/login`, `/register`
- **样式**: SCSS，`_variables.scss` 通过 Vite `additionalData` 全局注入
- **路径别名**: `@` → `src/`
- **自动导入**: `unplugin-auto-import` + `unplugin-vue-components`（Element Plus 组件按需导入）
- **E2E 测试**: Playwright，测试目录 `tests/e2e/`

核心文件：
- `src/api/http.ts` — Axios 封装（get/post/upload/download）
- `src/api/baseUrl.ts` — API Base URL 代码常量
- `src/utils/auth.ts` — Cookie token 管理（js-cookie，key: `vue3_token`）
- `src/utils/permission.ts` — 路由守卫
- `src/store/store.ts` — 用户状态（token, userName, avatar, role）
- `src/assets/style/_variables.scss` — 设计 token 和 mixin

### 后端 (`backend/`)

- **技术栈**: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic
- **三层泛型**: `SQLAlchemy Base → CRUDBase[Model, Create, Update] → CRUDRouter`
- **认证**: JWT（python-jose）+ bcrypt
- **数据库**: SQLite（默认），配置写在代码中

核心模式：
- 新增实体：定义 model → schema → crud（继承 CRUDBase）→ endpoint → 在 `main.py` 注册路由
- 数据库会话：通过 FastAPI 依赖注入（`get_db` 生成器）
- 配置管理：`pydantic-settings` 保留类型校验，代码默认值可被环境变量覆盖，但不读取 `.env` 和文件密钥

## 开发命令

### 一键启停（推荐）

```powershell
.\start.ps1   # 启动前后端（自动清理端口占用）
.\stop.ps1    # 停止所有服务
```

### 前端

```powershell
cd fronted
pnpm install          # 安装依赖（使用 pnpm，非 npm）
pnpm dev              # 开发服务器 → http://localhost:3000
pnpm build:prod       # 生产构建
pnpm lint             # ESLint 修复
pnpm prettier         # 格式化
```

### 后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\uvicorn app.main:app --reload --port 8000   # → http://localhost:8000
.\venv\Scripts\pytest -v                                    # 运行测试
.\venv\Scripts\pytest -v ..\tests\api\test_users.py         # 单文件测试
```

Alembic 迁移：
```powershell
.\venv\Scripts\alembic revision --autogenerate -m "描述"
.\venv\Scripts\alembic upgrade head
```

## 前后端联调

- 前端: `http://localhost:3000`，后端: `http://localhost:8000`
- Vite 代理: `/api/*` → `http://localhost:8000`
- 登录: `POST /api/v1/users/login`（JSON: `{email, password}`）
- 注册: `POST /api/v1/users/`（JSON: `{email, password, full_name}`）

## API 文档

后端运行时可访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Codex Skills

`.Codex/skills/` 中的自定义技能：
- `/init-vue3-frontend` — 使用 pnpm 创建 Vue 3 + TS + Pinia 项目
- `/init-fastapi-backend` — 创建 FastAPI + SQLAlchemy 项目，含泛型 CRUD

## 项目约定

- 前端包管理器：pnpm
- 后端使用 `venv/` 虚拟环境，`__init__.py` 均为空
- 前后端默认配置写入代码；后端部署期可用环境变量覆盖敏感和运行时配置；不使用 `.env`/`.env.example`
- Python 命令在 Windows 上使用 `.\venv\Scripts\` 前缀（非 `source venv/bin/activate`）

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Agent-Platform** (2952 symbols, 4772 relationships, 125 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Agent-Platform/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Agent-Platform/clusters` | All functional areas |
| `gitnexus://repo/Agent-Platform/processes` | All execution flows |
| `gitnexus://repo/Agent-Platform/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
