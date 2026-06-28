import json

from app.models.performance import Performance


def data(response):
    return response.json()["data"]


def test_performance_analyze_list_detail_delete_and_not_found(client, db):
    analyze_response = client.post(
        "/api/v1/performance/analyze",
        json={
            "project_id": 301,
            "name": "登录接口压测",
            "scenario": "高峰登录",
            "raw_text": "avg 860ms, P95 1700ms, error 2.5%, throughput 180, CPU 76%",
            "metrics": [
                {"name": "p95", "value": 1700, "unit": "ms", "threshold": 1200},
                {"name": "error_rate", "value": 2.5, "unit": "%", "threshold": 1},
            ],
        },
    )
    assert analyze_response.status_code == 200
    task = data(analyze_response)
    assert task["agent_key"] == "performance"
    assert task["project_id"] == 301
    assert task["status"] == "queued"

    record = Performance(
        project_id=301,
        configs=json.dumps(
            {
                "name": "登录接口压测结果",
                "source": "jmeter",
                "scenario": "高峰登录",
                "raw_text": "p95 1700ms",
                "metrics": [{"name": "p95", "value": 1700, "unit": "ms", "threshold": 1200}],
                "analysis": {
                    "score": 62,
                    "summary": "P95 超过阈值",
                    "findings": [
                        {
                            "title": "响应时间偏高",
                            "severity": "high",
                            "description": "P95 超过 1200ms",
                            "suggestion": "检查登录接口数据库查询",
                        }
                    ],
                    "trends": ["高峰期延迟上升"],
                },
            },
            ensure_ascii=False,
        ),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    list_response = client.get("/api/v1/performance/", params={"project_id": 301})
    assert list_response.status_code == 200
    assert data(list_response)["items"][0]["configs"]["name"] == "登录接口压测结果"

    detail_response = client.get(f"/api/v1/performance/{record.id}")
    assert detail_response.status_code == 200
    assert data(detail_response)["configs"]["analysis"]["score"] == 62

    missing_detail = client.get("/api/v1/performance/999999")
    assert missing_detail.status_code == 200
    assert missing_detail.json()["code"] == 404

    delete_response = client.delete(f"/api/v1/performance/{record.id}")
    assert delete_response.status_code == 200

    missing_delete = client.delete("/api/v1/performance/999999")
    assert missing_delete.status_code == 200
    assert missing_delete.json()["code"] == 404