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
    root = root_response.json()
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
    child = child_response.json()
    assert child["parent_id"] == root["id"]

    list_response = client.get("/api/v1/documents/", params={"project_id": 7})
    assert list_response.status_code == 200
    assert [item["name"] for item in list_response.json()] == ["功能性需求", "系统登录功能"]

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
    findings = review_response.json()["findings"]
    assert len(findings) >= 5
    assert findings[0]["title"] == "缺少登录成功后的跳转逻辑说明"

    update_response = client.put(
        f"/api/v1/documents/{child['id']}",
        json={
            "content": child["content"] + "\n补充：登录成功后进入系统主页。",
            "ai_suggest": [findings[0]],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["ai_suggest"][0]["title"] == findings[0]["title"]

    delete_response = client.delete(f"/api/v1/documents/{child['id']}")
    assert delete_response.status_code == 200
