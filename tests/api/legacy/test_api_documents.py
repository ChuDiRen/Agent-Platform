def test_create_api_document_and_analyze(client, response_data):
    parent_response = client.post(
        "/api/v1/api-documents/",
        json={
            "project_id": 1,
            "name": "接口文档目录",
            "title": "接口文档目录",
            "is_directory": True,
        },
    )
    assert parent_response.status_code == 200
    parent = response_data(parent_response)

    document_response = client.post(
        "/api/v1/api-documents/",
        json={
            "project_id": 1,
            "parent_id": parent["id"],
            "name": "接口文档",
            "title": "接口文档",
            "content": "# 接口信息\n\n请求 URL: /api/example\n\n请求方式: POST",
            "is_directory": False,
        },
    )
    assert document_response.status_code == 200
    document = response_data(document_response)
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
    task = response_data(analysis_response)
    assert task["agent_key"] == "api_document"
    assert task["status"] == "queued"

    update_response = client.put(
        f"/api/v1/api-documents/{document['id']}",
        json={
            "ai_suggest": [
                {
                    "id": "missing-response-params",
                    "title": "补充响应参数",
                    "description": "响应参数缺少字段说明",
                }
            ]
        },
    )
    assert update_response.status_code == 200
    assert response_data(update_response)["ai_suggest"][0]["title"]
