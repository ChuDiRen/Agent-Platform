def test_performance_analyze_list_detail_delete(client):
    response = client.post(
        "/api/v1/performance/analyze",
        json={
            "project_id": 1,
            "name": "登录链路压测分析",
            "scenario": "互联网小说网站登录压测",
            "raw_text": "avg 860ms, P95 1700ms, error 2.5%, throughput 180, CPU 76%",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["analysis"]["score"] < 100
    assert body["record"]["configs"]["metrics"]
    record_id = body["record"]["id"]

    list_response = client.get("/api/v1/performance/", params={"project_id": 1})
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == record_id

    detail_response = client.get(f"/api/v1/performance/{record_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["configs"]["analysis"]["findings"]

    delete_response = client.delete(f"/api/v1/performance/{record_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == record_id
