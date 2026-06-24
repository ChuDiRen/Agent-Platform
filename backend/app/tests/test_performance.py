def test_performance_analyze_list_detail_delete(client, response_data):
    response = client.post(
        "/api/v1/performance/analyze",
        json={
            "project_id": 1,
            "name": "性能分析",
            "scenario": "核心接口压测",
            "raw_text": "avg 860ms, P95 1700ms, error 2.5%, throughput 180, CPU 76%",
        },
    )
    assert response.status_code == 200
    task = response_data(response)
    assert task["agent_key"] == "performance"
    assert task["status"] == "queued"

    list_response = client.get("/api/v1/performance/", params={"project_id": 1})
    assert list_response.status_code == 200
    assert response_data(list_response)["items"] == []
