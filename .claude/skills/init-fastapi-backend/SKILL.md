---
name: init-fastapi-backend
description: 初始化 FastAPI + SQLAlchemy + Pydantic + Alembic 后端项目，包含泛型 CRUD、数据库迁移、Docker 容器化等完整工程化配置
user_invocable: true
---

# FastAPI + SQLAlchemy 后端项目初始化

## 触发条件
用户要求创建/初始化 FastAPI 后端项目、Python API 项目、后端脚手架时触发。

## 执行流程

### 阶段一：收集项目信息

向用户确认以下信息（如果未指定则使用默认值）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 项目名称 | `my-fastapi-app` | 项目文件夹名 |
| 数据库 | `sqlite` | sqlite / postgresql / mysql |
| 是否需要 Alembic 迁移 | 是 | 数据库版本管理 |
| 是否需要 Docker | 是 | 容器化部署 |
| 端口号 | `8000` | API 服务端口 |
| API 前缀 | `/api/v1` | 路由前缀 |

### 阶段二：创建项目结构

```bash
mkdir -p <项目名称>
cd <项目名称>
```

目录结构：

```
<项目名称>/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # 通用 CRUDRouter 泛型
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── users.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py              # 泛型 CRUD 基类
│   │   └── user.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py              # 导入所有模型以创建表
│   │   ├── base_class.py        # SQLAlchemy 声明式基类
│   │   └── session.py           # 数据库引擎和会话
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_main.py
│   │   └── test_users.py
│   └── utils/
│       ├── __init__.py
│       └── utils.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 阶段三：创建虚拟环境并安装依赖

```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

#### `requirements.txt`

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

#### `requirements-dev.txt`

```
-r requirements.txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
```

### 阶段四：写入源码文件

#### 4.1 `app/core/config.py`

```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI App"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "sqlite:///./test.db"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

#### 4.2 `app/core/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

#### 4.3 `app/db/base_class.py`

```python
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
```

#### 4.4 `app/db/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

#### 4.5 `app/db/base.py`

```python
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa: 新增模型后在此导入
```

#### 4.6 `app/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 4.7 `app/schemas/user.py`

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

#### 4.8 `app/crud/base.py`（泛型 CRUD 基类）

```python
from typing import Any, Generic, Type, TypeVar, Optional
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

#### 4.9 `app/crud/user.py`

```python
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
```

#### 4.10 `app/api/deps.py`（泛型路由基类）

```python
from typing import Any, Generic, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud.base import CRUDBase
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        crud: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
        prefix: str = "",
        tag: str = "",
    ):
        self.crud = crud
        self.router = APIRouter(prefix=prefix, tags=[tag] if tag else [])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/", response_model=Any)
        def create_item(obj_in: CreateSchemaType, db: Session = Depends(get_db)):
            return self.crud.create(db, obj_in=obj_in)

        @self.router.get("/{item_id}", response_model=Any)
        def read_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.get("/", response_model=list[Any])
        def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return self.crud.get_multi(db, skip=skip, limit=limit)

        @self.router.put("/{item_id}", response_model=Any)
        def update_item(
            item_id: int, obj_in: UpdateSchemaType, db: Session = Depends(get_db)
        ):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.update(db, db_obj=item, obj_in=obj_in)

        @self.router.delete("/{item_id}", response_model=Any)
        def delete_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.remove(db, id=item_id)
```

#### 4.11 `app/api/v1/endpoints/users.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.user import user as user_crud
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import create_access_token

router = APIRouter()


@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = user_crud.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create(db, obj_in=user_in)


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update(db, db_obj=user, obj_in=user_in)


@router.delete("/{user_id}", response_model=User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.remove(db, id=user_id)


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = user_crud.authenticate(db, email=email, password=password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
```

#### 4.12 `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import users

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
def health():
    return {"status": "ok"}
```

#### 4.13 `app/__init__.py`、`app/core/__init__.py`、`app/api/__init__.py` 等

所有 `__init__.py` 均为空文件。

#### 4.14 `app/tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.api.deps import get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
```

#### 4.15 `app/tests/test_main.py`

```python
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

#### 4.16 `app/tests/test_users.py`

```python
def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "testpass123", "full_name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_read_users(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### 阶段五：环境变量

#### `.env`

```
PROJECT_NAME=My FastAPI App
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=change-me-in-production-please
DEBUG=true
```

#### `.env.example`

```
PROJECT_NAME=My FastAPI App
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
DEBUG=false
```

### 阶段六：Alembic 数据库迁移

```bash
alembic init alembic
```

#### `alembic/env.py` 关键修改

在 `env.py` 的 `target_metadata` 处导入模型：

```python
from app.db.base import Base
target_metadata = Base.metadata
```

在 `run_migrations_online` 中设置数据库 URL：

```python
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

常用命令：

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
alembic downgrade -1
```

### 阶段七：Docker

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `docker-compose.yml`

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 阶段八：`.gitignore`

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
venv/
.env
*.db
.pytest_cache/
.mypy_cache/
alembic/versions/*.pyc
```

### 阶段九：验证

```bash
# 启动服务
uvicorn app.main:app --reload --port 8000

# 访问文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc

# 运行测试
pytest -v
```

## 架构设计要点

项目采用三层泛型抽象实现代码复用：

```
SQLAlchemy Base (models) → CRUDBase[Model, Create, Update] (crud) → CRUDRouter (api)
```

新增业务实体只需：
1. 定义 `models/xxx.py`（继承 Base）
2. 定义 `schemas/xxx.py`（Pydantic 模型）
3. 定义 `crud/xxx.py`（继承 CRUDBase）
4. 定义 `api/v1/endpoints/xxx.py`（使用 CRUDRouter）
5. 在 `main.py` 注册路由
6. 在 `db/base.py` 导入模型

## 输出清单

完成后告知用户：
1. 项目目录结构
2. 已安装的依赖
3. 启动命令（`uvicorn app.main:app --reload`）
4. API 文档地址（`/docs`、`/redoc`）
5. 测试命令（`pytest`）
6. 如需扩展新实体的步骤说明
