# Backend — CLAUDE.md

FastAPI REST API，三层泛型 CRUD 架构。

## 技术栈

FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic + SQLite

## 目录结构

```
app/
├── main.py              # 入口，CORS 中间件 + 路由注册
├── core/
│   ├── config.py        # pydantic-settings 配置（仅代码默认值）
│   └── security.py      # JWT + bcrypt
├── db/
│   ├── base_class.py    # SQLAlchemy 声明式基类（自动表名）
│   ├── base.py          # 导入所有 model（供 Alembic 发现）
│   └── session.py       # engine + SessionLocal
├── models/              # SQLAlchemy 模型
│   └── user.py
├── schemas/             # Pydantic schema
│   └── user.py
├── crud/                # 泛型 CRUD
│   ├── base.py          # CRUDBase[Model, Create, Update]
│   └── user.py          # CRUDUser + 模块级单例
├── api/
│   ├── deps.py          # get_db 依赖注入
│   └── v1/endpoints/    # 路由处理器
│       └── users.py
└── utils/
    └── utils.py         # generate_random_string
```

## 核心模式

**新增实体流程**：
1. `app/models/` 定义 SQLAlchemy model
2. `app/schemas/` 定义 Pydantic schema（Base → Create → Update → InDB → Response）
3. `app/crud/` 继承 `CRUDBase`，导出模块级单例
4. `app/api/v1/endpoints/` 写路由处理器
5. `app/main.py` 注册路由
6. `app/db/base.py` 导入新 model（Alembic 发现用）

**泛型 CRUD 继承链**：
```
CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]
  ├── get / get_multi / create / update / remove
  └── CRUDUser 扩展: get_by_email / authenticate / is_active / is_superuser
```

**认证**：JWT（python-jose）+ bcrypt（passlib），`create_access_token` 在 `core/security.py`

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/users/` | 注册（检查重复邮箱） |
| POST | `/api/v1/users/login` | 登录，返回 JWT + user |
| GET | `/api/v1/users/` | 用户列表（skip/limit） |
| GET | `/api/v1/users/{user_id}` | 获取单个用户 |
| PUT | `/api/v1/users/{user_id}` | 更新用户 |
| DELETE | `/api/v1/users/{user_id}` | 删除用户 |
| GET | `/` | 欢迎消息 |
| GET | `/health` | 健康检查 |

## 开发命令

```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
.\venv\Scripts\pytest -v
.\venv\Scripts\pytest -v ..\tests\api\test_users.py   # 单文件
```

Alembic 迁移：
```powershell
.\venv\Scripts\alembic revision --autogenerate -m "描述"
.\venv\Scripts\alembic upgrade head
```

Docker：
```powershell
docker-compose up --build
```

## 配置

后端配置统一写在 `app/core/config.py` 的 `Settings` 默认值中。`Settings` 保留
`pydantic-settings` 类型校验能力，但禁用环境变量、`.env` 和文件密钥配置源。

## 约定

- 所有 `__init__.py` 为空（仅命名空间）
- CRUD 单例在模块级导出（`user = CRUDUser(User)`）
- 数据库会话通过 FastAPI 依赖注入（`get_db` 生成器）
- 测试统一放在仓库根目录 `tests/`，API 测试使用独立 SQLite DB 并在 conftest 中覆盖 `get_db`
- API 版本前缀：`/api/v1/`
- 中文注释和错误消息
