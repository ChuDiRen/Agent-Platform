# Backend — CLAUDE.md

FastAPI REST API，三层泛型 CRUD 架构。

## 技术栈

FastAPI + SQLAlchemy 2.0 + Pydantic v2 + SQLite

## 目录结构

```
app/
├── main.py              # 入口，CORS 中间件 + 路由注册 + lifespan seed
├── core/
│   ├── config.py        # pydantic-settings 配置（仅代码默认值，敏感项必须环境变量覆盖）
│   ├── response.py      # 统一响应协议 {code,message,data}
│   └── security.py      # JWT + bcrypt
├── db/
│   ├── base_class.py    # SQLAlchemy 声明式基类（自动表名）
│   ├── base.py          # 导入所有 model（create_all 建表用）
│   └── session.py       # engine + SessionLocal（SQLite 启用外键 PRAGMA）
├── models/              # SQLAlchemy 模型（业务表均含 project_id 外键级联）
├── schemas/             # Pydantic schema
├── crud/                # 泛型 CRUD
│   ├── base.py          # CRUDBase[Model, Create, Update]
│   └── user.py          # CRUDUser + 模块级单例
├── api/
│   ├── deps.py          # get_db 依赖注入 + JWT 校验链
│   └── v1/endpoints/    # 路由处理器
├── agents/              # AI 智能体（DeepAgents + LangChain）
├── services/            # AgentTask 服务层
└── workers/             # Celery 任务（executor/registry/tasks）
```

## 核心模式

**新增实体流程**：
1. `app/models/` 定义 SQLAlchemy model
2. `app/schemas/` 定义 Pydantic schema（Base → Create → Update → Out）
3. `app/crud/` 继承 `CRUDBase`，导出模块级单例
4. `app/api/v1/endpoints/` 写路由处理器
5. `app/main.py` 注册路由
6. `app/db/base.py` 导入新 model（启动时 `create_all` 自动建表）

**数据库建表**：统一使用启动时 `Base.metadata.create_all`（main.py lifespan），**不使用 Alembic**；SQLite 通过 `PRAGMA foreign_keys=ON` 启用外键级联删除。

**泛型 CRUD 继承链**：
```
CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]
  ├── get / get_multi(按 id 倒序) / count / create / update / remove
  └── CRUDUser 扩展: get_by_email / authenticate / is_active / is_superuser
```

**认证**：JWT（python-jose）+ bcrypt（passlib），`create_access_token` 在 `core/security.py`。所有业务路由挂 `get_current_active_user`；用户管理接口按本人/admin 隔离；项目按 owner_id 数据隔离；AgentTask 的 user_id 由服务端绑定当前用户。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/users/` | 注册（检查重复邮箱） |
| POST | `/api/v1/users/login` | 登录，返回 JWT + user |
| GET | `/api/v1/users/` | 用户列表（admin） |
| GET | `/api/v1/users/{user_id}` | 获取单个用户（本人或 admin） |
| PUT | `/api/v1/users/{user_id}` | 更新用户（本人或 admin） |
| DELETE | `/api/v1/users/{user_id}` | 删除用户（admin） |
| POST | `/api/v1/projects/` | 创建项目（owner 绑定当前用户，密码 bcrypt 哈希存储） |
| POST | `/api/v1/projects/{id}/verify-password` | 服务端校验项目密码 |
| POST | `/api/v1/agent-tasks/` | 创建 AI 任务（user_id 服务端绑定） |
| GET | `/api/v1/agent-tasks/` | 任务列表（普通用户仅见自己的） |
| GET | `/api/v1/agent-tasks/{id}/events`、`/artifacts` | 任务事件/产物 |
| POST | `/api/v1/agent-tasks/{id}/cancel`、`/retry` | 取消/重试任务 |
| GET | `/` 欢迎；`/health` 健康检查 | 公开 |

## 开发命令

```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
.\venv\Scripts\pytest -v
.\venv\Scripts\pytest -v ..\tests\api\test_users.py   # 单文件
```

Docker：
```powershell
docker-compose up --build
```

## 配置

后端配置统一写在 `app/core/config.py` 的 `Settings` 默认值中。`Settings` 保留
`pydantic-settings` 类型校验能力，允许环境变量覆盖代码默认值，但不读取 `.env` 和文件密钥配置源。

## 约定

- 所有 `__init__.py` 为空（仅命名空间）
- CRUD 单例在模块级导出（`user = CRUDUser(User)`）
- 数据库会话通过 FastAPI 依赖注入（`get_db` 生成器）
- 测试统一放在仓库根目录 `tests/`，API 测试使用独立 SQLite DB 并在 conftest 中覆盖 `get_db`
- API 版本前缀：`/api/v1/`
- 中文注释和错误消息
