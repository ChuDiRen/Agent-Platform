"""基础路由测试（根路由 + 健康检查）。"""


def test_root(client):
    """GET / 应返回欢迎消息。"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "FastAPI" in data["message"] or "App" in data["message"]


def test_health(client):
    """GET /health 应返回状态 ok。"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_docs(client):
    """应能访问 OpenAPI 文档。"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/users/" in schema["paths"] or "/api/v1/users/login" in schema["paths"]
