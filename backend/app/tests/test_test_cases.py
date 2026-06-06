def test_generate_apply_and_manage_test_cases(client):
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
    generated = generate_response.json()["cases"]
    assert len(generated) >= 8
    assert generated[0]["module_id"] == 4101
    assert generated[0]["priority"] == 1
    assert "接口" in generated[0]["name"]
    assert "/api/user/login" in generated[0]["steps"]
    assert any(case["priority"] == 5 for case in generated)

    apply_response = client.post(
        "/api/v1/test-cases/apply",
        json={"cases": generated[:2]},
    )
    assert apply_response.status_code == 200
    saved = apply_response.json()
    assert len(saved) == 2
    assert saved[0]["id"]

    list_response = client.get("/api/v1/test-cases/", params={"module_id": 4101})
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    update_response = client.put(
        f"/api/v1/test-cases/{saved[0]['id']}",
        json={"name": "用户名为有效字母且长度在4-16字符内，注册成功", "priority": 1},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"].startswith("用户名为有效字母")

    delete_response = client.delete(f"/api/v1/test-cases/{saved[1]['id']}")
    assert delete_response.status_code == 200

    final_list_response = client.get("/api/v1/test-cases/", params={"module_id": 4101})
    assert len(final_list_response.json()) == 1
