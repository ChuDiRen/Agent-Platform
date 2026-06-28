from io import BytesIO


def data(response):
    return response.json()["data"]


def test_api_document_crud_analysis_upload_and_not_found(client):
    parent_response = client.post(
        "/api/v1/api-documents/",
        json={
            "project_id": 101,
            "name": "接口文档目录",
            "title": "接口文档目录",
            "is_directory": True,
        },
    )
    assert parent_response.status_code == 200
    parent = data(parent_response)

    document_response = client.post(
        "/api/v1/api-documents/",
        json={
            "project_id": 101,
            "parent_id": parent["id"],
            "name": "用户登录接口",
            "title": "用户登录接口",
            "content": "POST /api/v1/users/login\n请求体包含 email 和 password",
            "is_directory": False,
        },
    )
    assert document_response.status_code == 200
    document = data(document_response)
    assert document["parent_id"] == parent["id"]

    list_response = client.get("/api/v1/api-documents/", params={"project_id": 101})
    assert [item["name"] for item in data(list_response)["items"]] == ["接口文档目录", "用户登录接口"]

    detail_response = client.get(f"/api/v1/api-documents/{document['id']}")
    assert detail_response.status_code == 200
    assert data(detail_response)["content"].startswith("POST /api/v1/users/login")

    analysis_response = client.post(
        "/api/v1/api-documents/analysis",
        json={
            "document_id": document["id"],
            "title": document["title"],
            "content": document["content"],
            "extra_prompt": "检查鉴权和错误码说明",
        },
    )
    assert analysis_response.status_code == 200
    task = data(analysis_response)
    assert task["agent_key"] == "api_document"
    assert task["status"] == "queued"
    assert task["input_payload"]["document_id"] == document["id"]

    upload_response = client.post(
        "/api/v1/api-documents/upload",
        data={"project_id": "101", "parent_id": str(parent["id"])},
        files={"file": ("login-api.md", BytesIO(b"# Login API\nPOST /login"), "text/markdown")},
    )
    assert upload_response.status_code == 200
    uploaded = data(upload_response)
    assert uploaded["name"] == "login-api"
    assert uploaded["parent_id"] == parent["id"]
    assert "POST /login" in uploaded["content"]

    empty_upload = client.post(
        "/api/v1/api-documents/upload",
        files={"file": ("empty.md", BytesIO(b""), "text/markdown")},
    )
    assert empty_upload.status_code == 200
    assert empty_upload.json()["code"] == 400

    unsupported_upload = client.post(
        "/api/v1/api-documents/upload",
        files={"file": ("api.exe", BytesIO(b"binary"), "application/octet-stream")},
    )
    assert unsupported_upload.status_code == 200
    assert unsupported_upload.json()["code"] == 400

    update_response = client.put(
        f"/api/v1/api-documents/{document['id']}",
        json={
            "ai_suggest": [
                {
                    "id": "missing-response",
                    "title": "补充响应参数",
                    "description": "响应参数缺少字段说明",
                    "severity": "medium",
                    "category": "接口文档规范",
                    "adopted": True,
                }
            ]
        },
    )
    assert data(update_response)["ai_suggest"][0]["adopted"] is True

    missing_response = client.get("/api/v1/api-documents/999999")
    assert missing_response.status_code == 200
    assert missing_response.json()["code"] == 404

    delete_response = client.delete(f"/api/v1/api-documents/{document['id']}")
    assert delete_response.status_code == 200