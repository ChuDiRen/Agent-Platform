def test_generate_test_data_defaults(client, monkeypatch):
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
    body = response.json()["data"]
    assert body["agent_key"] == "test_data"
    assert body["status"] == "queued"
    assert body["input_payload"]["count"] == 3
    assert body["input_payload"]["format"] == "json"


def test_generate_test_data_csv(client, monkeypatch):
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
    body = response.json()["data"]
    assert body["agent_key"] == "test_data"
    assert body["input_payload"]["format"] == "csv"


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
    created = create_response.json()["data"]
    assert created["fields"][1]["name"] == "username"

    list_response = client.get("/api/v1/test-data/templates/", params={"project_id": 12})
    assert list_response.status_code == 200
    assert list_response.json()["data"]["items"][0]["name"] == "test_data_templates"

    update_response = client.put(
        f"/api/v1/test-data/templates/{created['id']}",
        json={"count": 8, "fields": payload["fields"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["count"] == 8

    delete_response = client.delete(f"/api/v1/test-data/templates/{created['id']}")
    assert delete_response.status_code == 200
