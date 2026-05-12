import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base_class import Base
from app.api.deps import get_db

# 使用内存数据库 + StaticPool，保证所有连接共享同一个数据库
# 这样测试更干净、更快，不产生文件残留
engine = create_engine(
    "sqlite://",  # 内存数据库
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """每个测试函数独立的数据库会话，测试前建表，测试后清表。"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """每个测试函数独立的 FastAPI TestClient。"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def create_user_via_api(client):
    """辅助 fixture：通过 API 创建用户并返回响应数据。"""
    def _create(email="test@example.com", password="testpass123", full_name="Test User"):
        response = client.post(
            "/api/v1/users/",
            json={"email": email, "password": password, "full_name": full_name},
        )
        return response
    return _create


@pytest.fixture
def auth_headers(client, create_user_via_api):
    """辅助 fixture：创建用户并登录，返回带 Authorization 的请求头。"""
    create_user_via_api()
    response = client.post(
        "/api/v1/users/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
