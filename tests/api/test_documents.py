def test_document_tree_and_review_round_trip(client):
    root_response = client.post(
        "/api/v1/documents/",
        json={
            "project_id": 7,
            "name": "功能性需求",
            "title": "功能性需求",
            "is_directory": True,
        },
    )
    assert root_response.status_code == 200
    root = root_response.json()["data"]
    assert root["is_directory"] is True

    content = """
# 功能性需求
## 系统登录功能
功能概述：出租屋管理系统登录功能，提供用户身份验证入口，确保系统访问安全。
功能入口：系统首页或直接访问登录URL时展示的登录表单。
界面原型：账号输入框、密码输入框、登录按钮。
"""
    child_response = client.post(
        "/api/v1/documents/",
        json={
            "project_id": 7,
            "parent_id": root["id"],
            "name": "系统登录功能",
            "title": "系统登录功能",
            "content": content,
            "is_directory": False,
        },
    )
    assert child_response.status_code == 200
    child = child_response.json()["data"]
    assert child["parent_id"] == root["id"]

    list_response = client.get("/api/v1/documents/", params={"project_id": 7})
    assert list_response.status_code == 200
    assert [item["name"] for item in list_response.json()["data"]["items"]] == ["功能性需求", "系统登录功能"]

    review_response = client.post(
        "/api/v1/documents/review",
        json={
            "document_id": child["id"],
            "title": child["title"],
            "content": child["content"],
            "extra_prompt": "请重点关注登录安全和跳转逻辑",
        },
    )
    assert review_response.status_code == 200
    review_task = review_response.json()["data"]
    assert review_task["agent_key"] == "requirement_review"
    assert review_task["status"] == "queued"
    assert review_task["input_payload"]["document_id"] == child["id"]

    findings = [
        {
            "id": "finding-0",
            "title": "缺少登录成功后的跳转逻辑说明",
            "description": "补充登录成功后的目标页面。",
            "severity": "medium",
            "category": "流程完整性",
            "adopted": True,
        }
    ]

    update_response = client.put(
        f"/api/v1/documents/{child['id']}",
        json={
            "content": child["content"] + "\n补充：登录成功后进入系统主页。",
            "ai_suggest": [findings[0]],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["ai_suggest"][0]["title"] == findings[0]["title"]

    delete_response = client.delete(f"/api/v1/documents/{child['id']}")
    assert delete_response.status_code == 200


def test_requirement_review_exposes_only_current_task_endpoint(client):
    payload = {
        "title": "登录需求",
        "content": "用户输入账号密码后登录系统。",
    }

    current_response = client.post("/api/v1/documents/review", json=payload)
    assert current_response.status_code == 200
    assert current_response.json()["data"]["agent_key"] == "requirement_review"

    async_response = client.post("/api/v1/documents/review/async", json=payload)
    stream_response = client.post("/api/v1/documents/review/stream", json=payload)

    assert async_response.status_code == 404
    assert stream_response.status_code == 404
