def test_create_api_document_and_analyze(client):
    parent_response = client.post(
        "/api/v1/api-documents/",
        json={
            "project_id": 1,
            "name": "学生端登录接口文档",
            "title": "学生端登录接口文档",
            "is_directory": True,
        },
    )
    assert parent_response.status_code == 200
    parent = parent_response.json()

    document_response = client.post(
        "/api/v1/api-documents/",
        json={
            "project_id": 1,
            "parent_id": parent["id"],
            "name": "学生端登录接口文档20050830",
            "title": "学生端登录接口文档20050830",
            "content": "# 接口信息\n\n请求 URL: /api/user/login\n\n请求方式: POST",
            "is_directory": False,
        },
    )
    assert document_response.status_code == 200
    document = document_response.json()
    assert document["parent_id"] == parent["id"]

    analysis_response = client.post(
        "/api/v1/api-documents/analysis",
        json={
            "document_id": document["id"],
            "title": document["title"],
            "content": document["content"],
        },
    )
    assert analysis_response.status_code == 200
    findings = analysis_response.json()["findings"]
    assert findings
    assert any(item["id"] == "missing-response-params" for item in findings)

    update_response = client.put(
        f"/api/v1/api-documents/{document['id']}",
        json={"ai_suggest": findings},
    )
    assert update_response.status_code == 200
    assert update_response.json()["ai_suggest"][0]["title"]
