import json

from app.models.api_test_cases_exec import ApiTestCasesExec
from app.models.ui_test_cases_exec import UiTestCasesExec


def data(response):
    return response.json()["data"]


def test_api_automation_cases_execs_copy_delete_and_not_found(client, db):
    cases_response = client.get("/api/v1/api-automation/cases", params={"project_id": 401})
    assert cases_response.status_code == 200
    assert data(cases_response) == []

    missing_case = client.get("/api/v1/api-automation/cases/10001")
    assert missing_case.status_code == 200
    assert missing_case.json()["code"] == 404

    missing_run = client.post(
        "/api/v1/api-automation/execs",
        json={
            "project_id": 401,
            "name": "登录接口自动化执行",
            "case_ids": [10001],
            "exec_param": {"baseUrl": "http://localhost:8000"},
        },
    )
    assert missing_run.status_code == 200
    assert missing_run.json()["code"] == 404

    exec_record = ApiTestCasesExec(
        project_id=401,
        name="历史登录接口执行",
        exec_type="HTTP 请求",
        case_ids=json.dumps([10001]),
        details=json.dumps({"summary": {"success": 1, "failed": 0, "total": 1}, "results": []}),
        desc="真实业务历史执行记录",
        exec_param=json.dumps({"baseUrl": "http://localhost:8000"}),
        exec_status="已完成",
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)

    list_response = client.get("/api/v1/api-automation/execs", params={"project_id": 401})
    assert data(list_response)["items"][0]["name"] == "历史登录接口执行"

    detail_response = client.get(f"/api/v1/api-automation/execs/{exec_record.id}")
    assert data(detail_response)["details"]["summary"]["total"] == 1

    copy_response = client.post(f"/api/v1/api-automation/execs/{exec_record.id}/copy")
    assert copy_response.status_code == 200
    copied = data(copy_response)
    assert copied["name"] == "历史登录接口执行-复制执行"

    missing_copy = client.post("/api/v1/api-automation/execs/999999/copy")
    assert missing_copy.status_code == 200
    assert missing_copy.json()["code"] == 404

    delete_response = client.delete(f"/api/v1/api-automation/execs/{exec_record.id}")
    assert delete_response.status_code == 200

    missing_delete = client.delete("/api/v1/api-automation/execs/999999")
    assert missing_delete.status_code == 200
    assert missing_delete.json()["code"] == 404


def test_ui_automation_cases_execs_copy_delete_and_not_found(client, db):
    cases_response = client.get("/api/v1/ui-automation/cases", params={"project_id": 402})
    assert cases_response.status_code == 200
    assert data(cases_response) == []

    missing_case = client.get("/api/v1/ui-automation/cases/509")
    assert missing_case.status_code == 200
    assert missing_case.json()["code"] == 404

    missing_run = client.post(
        "/api/v1/ui-automation/execs",
        json={
            "project_id": 402,
            "name": "登录页 UI 自动化执行",
            "case_ids": [509],
            "exec_param": {"browser": "chromium"},
        },
    )
    assert missing_run.status_code == 200
    assert missing_run.json()["code"] == 404

    exec_record = UiTestCasesExec(
        project_id=402,
        name="历史登录 UI 执行",
        exec_type="WEB 网页",
        case_ids=json.dumps([509]),
        details=json.dumps({"summary": {"success": 1, "failed": 0, "total": 1}, "results": []}),
        desc="真实业务历史 UI 执行记录",
        exec_param=json.dumps({"browser": "chromium"}),
        exec_status="已完成",
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)

    list_response = client.get("/api/v1/ui-automation/execs", params={"project_id": 402})
    assert data(list_response)["items"][0]["name"] == "历史登录 UI 执行"

    detail_response = client.get(f"/api/v1/ui-automation/execs/{exec_record.id}")
    assert data(detail_response)["details"]["summary"]["total"] == 1

    copy_response = client.post(f"/api/v1/ui-automation/execs/{exec_record.id}/copy")
    copied = data(copy_response)
    assert copied["name"] == "历史登录 UI 执行-复制执行"

    missing_copy = client.post("/api/v1/ui-automation/execs/999999/copy")
    assert missing_copy.status_code == 200
    assert missing_copy.json()["code"] == 404

    delete_response = client.delete(f"/api/v1/ui-automation/execs/{exec_record.id}")
    assert delete_response.status_code == 200

    missing_delete = client.delete("/api/v1/ui-automation/execs/999999")
    assert missing_delete.status_code == 200
    assert missing_delete.json()["code"] == 404