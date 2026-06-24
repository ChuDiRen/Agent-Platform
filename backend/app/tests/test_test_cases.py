def test_generate_test_cases_creates_agent_task(client, response_data):
    generate_response = client.post(
        "/api/v1/test-cases/generate",
        json={
            "project_id": 1,
            "module": {
                "id": 4101,
                "title": "4.1 用户注册 bbs-register-001",
                "content": "用户必须在系统进行注册，拥有BBS账户之后，才能够使用相关的功能。",
            },
            "extra_requirement": "覆盖用户名长度、密码确认和重复提交",
        },
    )

    assert generate_response.status_code == 200
    task = response_data(generate_response)
    assert task["agent_key"] == "test_case"
    assert task["project_id"] == 1
    assert task["status"] == "queued"


def test_apply_and_manage_test_cases(client, response_data):
    cases = [
        {
            "project_id": 1,
            "module_id": 4101,
            "module_name": "用户注册",
            "name": "用户名为有效字母且长度在4-16字符内，注册成功",
            "priority": 1,
            "case_type": "接口",
            "preconditions": "用户未注册",
            "steps": "POST /api/user/login",
            "expected": "注册成功",
            "tags": ["接口", "注册"],
        },
        {
            "project_id": 1,
            "module_id": 4101,
            "module_name": "用户注册",
            "name": "重复提交注册请求时提示用户已存在",
            "priority": 5,
            "case_type": "接口",
            "preconditions": "用户已注册",
            "steps": "POST /api/user/login",
            "expected": "提示重复注册",
            "tags": ["接口", "异常"],
        },
    ]

    apply_response = client.post("/api/v1/test-cases/apply", json={"cases": cases})
    assert apply_response.status_code == 200
    saved = response_data(apply_response)
    assert len(saved) == 2
    assert saved[0]["id"]

    list_response = client.get("/api/v1/test-cases/", params={"module_id": 4101})
    assert list_response.status_code == 200
    listed = response_data(list_response)
    assert len(listed["items"]) == 2

    update_response = client.put(
        f"/api/v1/test-cases/{saved[0]['id']}",
        json={"name": "用户名为有效字母且长度在4-16字符内，注册成功", "priority": 1},
    )
    assert update_response.status_code == 200
    assert response_data(update_response)["name"].startswith("用户名为有效字母")

    delete_response = client.delete(f"/api/v1/test-cases/{saved[1]['id']}")
    assert delete_response.status_code == 200

    final_list_response = client.get("/api/v1/test-cases/", params={"module_id": 4101})
    assert len(response_data(final_list_response)["items"]) == 1
