def data(response):
    return response.json()["data"]


def test_generate_apply_manage_test_cases_and_not_found(client):
    generate_response = client.post(
        "/api/v1/test-cases/generate",
        json={
            "project_id": 201,
            "module": {
                "id": 4101,
                "title": "用户注册",
                "content": "用户提交邮箱、密码和确认密码后完成注册。",
            },
            "extra_requirement": "覆盖重复邮箱、密码长度和确认密码不一致",
        },
    )
    assert generate_response.status_code == 200
    task = data(generate_response)
    assert task["agent_key"] == "test_case"
    assert task["project_id"] == 201
    assert task["status"] == "queued"

    create_response = client.post(
        "/api/v1/test-cases/",
        json={
            "project_id": 201,
            "module_id": 4101,
            "name": "邮箱和密码合法时注册成功",
            "priority": 1,
            "precondition": "邮箱未注册",
            "steps": "打开注册页，输入合法邮箱和密码，点击注册",
            "expected": "注册成功并跳转登录页",
        },
    )
    assert create_response.status_code == 200
    created = data(create_response)
    assert created["module_id"] == 4101

    cases = [
        {
            "project_id": 201,
            "module_id": 4101,
            "name": "重复邮箱注册失败",
            "priority": 2,
            "precondition": "邮箱已注册",
            "steps": "使用已注册邮箱提交注册",
            "expected": "提示邮箱已存在",
        },
        {
            "project_id": 201,
            "module_id": 4101,
            "name": "确认密码不一致注册失败",
            "priority": 3,
            "precondition": "用户在注册页",
            "steps": "输入不同的密码和确认密码",
            "expected": "前端提示两次密码不一致",
        },
    ]
    apply_response = client.post("/api/v1/test-cases/apply", json={"cases": cases})
    assert apply_response.status_code == 200
    saved = data(apply_response)
    assert len(saved) == 2

    list_response = client.get("/api/v1/test-cases/", params={"module_id": 4101})
    listed = data(list_response)["items"]
    assert {item["name"] for item in listed} == {
        "邮箱和密码合法时注册成功",
        "重复邮箱注册失败",
        "确认密码不一致注册失败",
    }

    detail_response = client.get(f"/api/v1/test-cases/{created['id']}")
    assert detail_response.status_code == 200
    assert data(detail_response)["name"] == "邮箱和密码合法时注册成功"

    update_response = client.put(
        f"/api/v1/test-cases/{created['id']}",
        json={"priority": 2, "expected": "注册成功后展示登录入口"},
    )
    assert data(update_response)["priority"] == 2
    assert data(update_response)["expected"] == "注册成功后展示登录入口"

    missing_detail = client.get("/api/v1/test-cases/999999")
    assert missing_detail.status_code == 200
    assert missing_detail.json()["code"] == 404

    missing_update = client.put("/api/v1/test-cases/999999", json={"name": "不存在"})
    assert missing_update.status_code == 200
    assert missing_update.json()["code"] == 404

    delete_response = client.delete(f"/api/v1/test-cases/{saved[0]['id']}")
    assert delete_response.status_code == 200

    missing_delete = client.delete("/api/v1/test-cases/999999")
    assert missing_delete.status_code == 200
    assert missing_delete.json()["code"] == 404