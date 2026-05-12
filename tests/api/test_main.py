"""基础路由测试（根路由 + 健康检查）。

基于 playwright-best-practices 最佳实践：
- 按功能分组测试
- 清晰的测试命名
- 完整的断言
"""

import pytest


@pytest.mark.smoke
class TestRootRoutes:
    """基础路由测试。"""

    def test_root(self, client):
        """GET / 应返回欢迎消息。"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "FastAPI" in data["message"] or "App" in data["message"]

    def test_health(self, client):
        """GET /health 应返回状态 ok。"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.smoke
class TestOpenAPI:
    """OpenAPI 文档测试。"""

    def test_openapi_docs(self, client):
        """应能访问 OpenAPI 文档。"""
        response = client.get("/api/v1/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/users/" in schema["paths"] or "/api/v1/users/login" in schema["paths"]
