def test_api_automation_create_list_copy_delete(client):
    cases_response = client.get("/api/v1/api-automation/cases", params={"project_id": 1})
    assert cases_response.status_code == 200
    cases = cases_response.json()
    assert len(cases) >= 2
    assert cases[0]["exec_type"] == "HTTP 请求"
    assert cases[0]["request"]["path"] == "/user/login"

    detail_response = client.get(f"/api/v1/api-automation/cases/{cases[0]['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["expected"]

    create_response = client.post(
        "/api/v1/api-automation/execs",
        json={
            "project_id": 1,
            "name": "互联网小说网站登录接口冒烟测试",
            "exec_type": "HTTP 请求",
            "case_ids": [cases[0]["id"], cases[1]["id"]],
            "exec_param": {
                "base_url": "http://novel.hctestedu.com",
                "credential": {"username": "18511114444", "password": "123456"},
            },
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["exec_status"] == "已完成"
    assert created["details"]["summary"]["total"] == 2
    assert created["details"]["summary"]["failed"] == 1
    assert "AI断言" in created["details"]["results"][0]["ai_record"]

    list_response = client.get("/api/v1/api-automation/execs", params={"project_id": 1})
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]

    copy_response = client.post(f"/api/v1/api-automation/execs/{created['id']}/copy")
    assert copy_response.status_code == 200
    assert copy_response.json()["name"].endswith("复制执行")

    delete_response = client.delete(f"/api/v1/api-automation/execs/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == created["id"]
