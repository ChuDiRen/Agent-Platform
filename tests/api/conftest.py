"""后端 API 测试配置。

基于 playwright-best-practices 最佳实践：
- 使用工厂模式创建测试数据
- Fixtures 提供隔离和复用
- 每个测试函数独立的数据库会话
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Callable

# 将 backend 目录添加到 Python 路径
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.api.deps import get_db


# ============================================================
# 测试数据工厂
# ============================================================

class UserFactory:
    """用户数据工厂，支持创建不同类型的用户。"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    _SENTINEL = object()

    @classmethod
    def create(
        cls,
        email: str | None = None,
        password: str = "SecurePass123!",
        full_name: str | None | object = _SENTINEL,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> dict:
        """创建用户数据字典。"""
        idx = cls._next_id()
        result = {
            "email": email or f"user{idx}@example.com",
            "password": password,
        }
        # 只有未显式传 full_name 时才设置默认值
        if full_name is not cls._SENTINEL:
            result["full_name"] = full_name
        else:
            result["full_name"] = f"测试用户{idx}"
        return result

    @classmethod
    def create_admin(cls, **kwargs) -> dict:
        """创建管理员用户数据。"""
        defaults = {
            "email": f"admin{cls._next_id()}@company.com",
            "password": "AdminPass123!",
            "full_name": f"管理员{cls._counter}",
        }
        defaults.update(kwargs)
        return cls.create(**defaults)

    @classmethod
    def create_minimal(cls, **kwargs) -> dict:
        """创建最小数据（仅必填字段，不含 full_name）。"""
        idx = cls._next_id()
        defaults = {
            "email": f"minimal{idx}@example.com",
            "password": "MinimalPass123!",
            "full_name": None,
        }
        defaults.update(kwargs)
        return cls.create(**defaults)


@pytest.fixture
def user_factory() -> type[UserFactory]:
    """提供用户数据工厂。"""
    UserFactory._counter = 0
    return UserFactory


# ============================================================
# 数据库 Fixtures
# ============================================================

@pytest.fixture(scope="function")
def db_path() -> Generator[str, None, None]:
    """创建临时数据库文件，测试后删除。"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture(scope="function")
def engine(db_path):
    """创建真实 SQLite 文件数据库引擎。"""
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def SessionLocal(engine):
    """创建数据库会话工厂。"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db(SessionLocal) -> Generator:
    """每个测试函数独立的数据库会话。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(SessionLocal) -> Generator[TestClient, None, None]:
    """每个测试函数独立的 FastAPI TestClient。"""

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def disable_agent_task_delivery(monkeypatch):
    """API tests verify HTTP/database contracts without requiring Redis/Celery."""
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", lambda task_id: None)


# ============================================================
# API 操作 Fixtures
# ============================================================

@pytest.fixture
def create_user_via_api(client: TestClient) -> Callable:
    """辅助 fixture：通过 API 创建用户并返回响应。"""

    def _create(
        email: str = "testuser@example.com",
        password: str = "SecurePass123!",
        full_name: str = "测试用户",
    ) -> dict:
        response = client.post(
            "/api/v1/users/",
            json={"email": email, "password": password, "full_name": full_name},
        )
        return response

    return _create


@pytest.fixture
def create_and_login(client: TestClient, create_user_via_api: Callable) -> Callable:
    """辅助 fixture：创建用户并登录，返回 token 和用户信息。"""

    def _create_and_login(
        email: str = "auth@example.com",
        password: str = "AuthPass123!",
        full_name: str = "认证用户",
    ) -> dict:
        # 创建用户
        create_response = create_user_via_api(email=email, password=password, full_name=full_name)
        user_data = create_response.json()

        # 登录获取 token
        login_response = client.post(
            "/api/v1/users/login",
            json={"email": email, "password": password},
        )
        token_data = login_response.json()

        return {
            "user": user_data,
            "token": token_data["access_token"],
            "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
        }

    return _create_and_login


@pytest.fixture
def auth_headers(client: TestClient, create_user_via_api: Callable) -> dict:
    """辅助 fixture：创建用户并登录，返回带 Authorization 的请求头。"""
    create_user_via_api()
    response = client.post(
        "/api/v1/users/login",
        json={"email": "testuser@example.com", "password": "SecurePass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
