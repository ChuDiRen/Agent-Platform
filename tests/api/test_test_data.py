import json
import sys
from types import SimpleNamespace


class FakeDeepAgent:
    def invoke(self, payload):
        requested = payload["messages"][0]["content"]
        if '"name": "email"' in requested:
            rows = [{"email": "qa1@example.com"}, {"email": "qa2@example.com"}]
        else:
            rows = [
                {"id": 1, "username": "用户1", "pass": "密码1"},
                {"id": 2, "username": "用户2", "pass": "密码2"},
                {"id": 3, "username": "用户3", "pass": "密码3"},
            ]
        return {"messages": [SimpleNamespace(content=json.dumps(rows, ensure_ascii=False))]}


def install_fake_deepagents(monkeypatch):
    module = SimpleNamespace(create_deep_agent=lambda **kwargs: FakeDeepAgent())
    monkeypatch.setitem(sys.modules, "deepagents", module)
    monkeypatch.setenv("DEEPAGENTS_MODEL", "test:model")


def test_generate_test_data_defaults(client, monkeypatch):
    install_fake_deepagents(monkeypatch)

    response = client.post(
        "/api/v1/test-data/generate",
        json={
            "count": 3,
            "format": "json",
            "lang": "zh",
            "fields": [
                {"name": "id", "type": "number", "rule": "从1开始递增"},
                {"name": "username", "type": "string", "rule": "用户"},
                {"name": "pass", "type": "string", "rule": "密码"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert body["format"] == "json"
    assert body["data"][0] == {"id": 1, "username": "用户1", "pass": "密码1"}
    assert '"data"' in body["content"]


def test_generate_test_data_csv(client, monkeypatch):
    install_fake_deepagents(monkeypatch)

    response = client.post(
        "/api/v1/test-data/generate",
        json={
            "count": 2,
            "format": "csv",
            "lang": "en",
            "fields": [{"name": "email", "type": "email", "rule": "qa"}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["content"].splitlines() == ["email", "qa1@example.com", "qa2@example.com"]


def test_generate_test_data_requires_deepagents_model(client, monkeypatch):
    monkeypatch.delenv("DEEPAGENTS_MODEL", raising=False)

    response = client.post(
        "/api/v1/test-data/generate",
        json={
            "count": 1,
            "format": "json",
            "lang": "zh",
            "fields": [{"name": "id", "type": "number", "rule": "从1开始递增"}],
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "DEEPAGENTS_MODEL is not configured"


def test_template_crud_round_trip(client):
    payload = {
        "project_id": 12,
        "name": "test_data_templates",
        "description": "基础测试账号",
        "hint": "生成可登录用户",
        "count": 5,
        "format": "json",
        "lang": "zh",
        "fields": [
            {"name": "id", "type": "number", "rule": "从1开始递增"},
            {"name": "username", "type": "string", "rule": "用户"},
        ],
    }

    create_response = client.post("/api/v1/test-data/templates/", json=payload)
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["fields"][1]["name"] == "username"

    list_response = client.get("/api/v1/test-data/templates/", params={"project_id": 12})
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "test_data_templates"

    update_response = client.put(
        f"/api/v1/test-data/templates/{created['id']}",
        json={"count": 8, "fields": payload["fields"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["count"] == 8

    delete_response = client.delete(f"/api/v1/test-data/templates/{created['id']}")
    assert delete_response.status_code == 200
