# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述

Agent-Platform 是一个全栈 monorepo，前后端分离。采用 Apache 2.0 许可证。

## 架构

```
Agent-Platform/
├── fronted/          # Vue 3 单页应用（注意：目录名拼写为 "fronted"）
├── backend/          # FastAPI REST API
├── start.ps1         # 一键启动（自动清理端口占用）
├── stop.ps1          # 一键停止
└── .claude/skills/   # Claude Code 项目技能
```

> 各子项目详细文档见 [fronted/CLAUDE.md](fronted/CLAUDE.md) 和 [backend/CLAUDE.md](backend/CLAUDE.md)。

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
- `src/api/baseUrl.ts` — 环境 URL 区分
- `src/utils/auth.ts` — Cookie token 管理（js-cookie，key: `vue3_token`）
- `src/utils/permission.ts` — 路由守卫
- `src/store/store.ts` — 用户状态（token, userName, avatar, role）
- `src/assets/style/_variables.scss` — 设计 token 和 mixin

### 后端 (`backend/`)

- **技术栈**: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic
- **三层泛型**: `SQLAlchemy Base → CRUDBase[Model, Create, Update] → CRUDRouter`
- **认证**: JWT（python-jose）+ bcrypt
- **数据库**: SQLite（默认），`.env` 可配置

核心模式：
- 新增实体：定义 model → schema → crud（继承 CRUDBase）→ endpoint → 在 `main.py` 注册路由
- 数据库会话：通过 FastAPI 依赖注入（`get_db` 生成器）
- 配置管理：`pydantic-settings` 读取 `.env`

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
.\venv\Scripts\pytest -v app\tests\test_users.py            # 单文件测试
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

## Claude Skills

`.claude/skills/` 中的自定义技能：
- `/init-vue3-frontend` — 使用 pnpm 创建 Vue 3 + TS + Pinia 项目
- `/init-fastapi-backend` — 创建 FastAPI + SQLAlchemy 项目，含泛型 CRUD

## 项目约定

- 前端包管理器：pnpm
- 后端使用 `venv/` 虚拟环境，`__init__.py` 均为空
- `.env` 已 gitignore，`.env.example` 为模板
- Python 命令在 Windows 上使用 `.\venv\Scripts\` 前缀（非 `source venv/bin/activate`）
