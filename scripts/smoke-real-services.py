"""Smoke test the running Agent-Platform services through real HTTP calls."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


BASE_URL = "http://localhost:8000"
TASK_TIMEOUT_SECONDS = 60


class SmokeFailure(RuntimeError):
    pass


def unwrap(response: httpx.Response) -> Any:
    try:
        body = response.json()
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"{response.request.method} {response.request.url} returned non-JSON") from exc
    if response.status_code != 200:
        raise SmokeFailure(f"{response.request.method} {response.request.url} HTTP {response.status_code}: {body}")
    if body.get("code") != 0:
        raise SmokeFailure(f"{response.request.method} {response.request.url} API code {body.get('code')}: {body}")
    return body.get("data")


def wait_task(client: httpx.Client, task: dict[str, Any], label: str) -> dict[str, Any]:
    deadline = time.time() + TASK_TIMEOUT_SECONDS
    task_id = task["id"]
    while time.time() < deadline:
        current = unwrap(client.get(f"/api/v1/agent-tasks/{task_id}"))
        if current["status"] in {"succeeded", "failed", "cancelled"}:
            if current["status"] != "succeeded":
                raise SmokeFailure(f"{label} task #{task_id} ended as {current['status']}: {current.get('error_message')}")
            unwrap(client.get(f"/api/v1/agent-tasks/{task_id}/events"))
            unwrap(client.get(f"/api/v1/agent-tasks/{task_id}/artifacts"))
            return current
        time.sleep(1)
    raise SmokeFailure(f"{label} task #{task_id} timed out")


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    results: list[str] = []
    with httpx.Client(base_url=BASE_URL, timeout=15) as client:
        health = client.get("/health")
        if health.status_code != 200 or health.json().get("status") != "ok":
            raise SmokeFailure(f"health failed: {health.status_code} {health.text}")
        results.append("health")

        login = unwrap(client.post("/api/v1/users/login", json={"email": "admin@qq.com", "password": "admin123456"}))
        assert login["access_token"]
        results.append("login")

        project = unwrap(client.post("/api/v1/projects/", json={
            "name": f"Smoke Project {stamp}",
            "description": "real service smoke test",
        }))
        project_id = project["id"]
        unwrap(client.get(f"/api/v1/projects/{project_id}"))
        unwrap(client.put(f"/api/v1/projects/{project_id}", json={"description": "updated smoke project"}))
        unwrap(client.get("/api/v1/projects/"))
        results.append("projects")

        agents = unwrap(client.get("/api/v1/agents/"))
        if not agents:
            raise SmokeFailure("agents list is empty")
        results.append("agents")

        doc = unwrap(client.post("/api/v1/documents/", json={
            "project_id": project_id,
            "name": f"需求文档 {stamp}",
            "title": "登录需求",
            "content": "用户可以使用邮箱和密码登录，失败时提示错误原因。",
            "is_directory": False,
        }))
        unwrap(client.get(f"/api/v1/documents/{doc['id']}"))
        review_task = unwrap(client.post("/api/v1/documents/review", json={
            "document_id": doc["id"],
            "title": doc["title"],
            "content": doc["content"],
        }))
        wait_task(client, review_task, "requirement_review")
        results.append("documents + requirement_review")

        api_doc = unwrap(client.post("/api/v1/api-documents/", json={
            "project_id": project_id,
            "name": f"接口文档 {stamp}",
            "title": "登录接口",
            "content": "POST /api/v1/users/login request: email,password response: access_token",
            "is_directory": False,
        }))
        api_doc_task = unwrap(client.post("/api/v1/api-documents/analysis", json={
            "document_id": api_doc["id"],
            "title": api_doc["title"],
            "content": api_doc["content"],
        }))
        wait_task(client, api_doc_task, "api_document")
        results.append("api_documents + analysis")

        template = unwrap(client.post("/api/v1/test-data/templates/", json={
            "project_id": project_id,
            "name": f"用户数据模板 {stamp}",
            "fields": [{"name": "email", "type": "email"}, {"name": "age", "type": "number"}],
            "count": 2,
            "format": "json",
            "lang": "zh",
        }))
        unwrap(client.get(f"/api/v1/test-data/templates/{template['id']}"))
        test_data_task = unwrap(client.post("/api/v1/test-data/generate", json={
            "fields": [{"name": "email", "type": "email"}, {"name": "age", "type": "number"}],
            "count": 2,
            "format": "json",
            "lang": "zh",
        }))
        wait_task(client, test_data_task, "test_data")
        results.append("test_data")

        test_case_task = unwrap(client.post("/api/v1/test-cases/generate", json={
            "project_id": project_id,
            "module": {
                "id": 101,
                "title": "登录模块",
                "content": "用户输入邮箱和密码后可以登录系统。",
            },
            "extra_requirement": "覆盖正确密码和错误密码",
        }))
        wait_task(client, test_case_task, "test_case")
        saved_cases = unwrap(client.post("/api/v1/test-cases/apply", json={
            "cases": [{
                "project_id": project_id,
                "module_id": 101,
                "name": f"登录成功用例 {stamp}",
                "priority": 1,
                "precondition": "用户已注册",
                "steps": "输入正确邮箱和密码，点击登录",
                "expected": "登录成功",
            }]
        }))
        unwrap(client.get("/api/v1/test-cases/", params={"project_id": project_id}))
        unwrap(client.get(f"/api/v1/test-cases/{saved_cases[0]['id']}"))
        results.append("test_cases")

        perf_task = unwrap(client.post("/api/v1/performance/analyze", json={
            "project_id": project_id,
            "name": f"性能分析 {stamp}",
            "scenario": "登录接口压测",
            "raw_text": "avg 860ms, p95 1700ms, error 2.5%, throughput 180, CPU 76%",
            "metrics": [{"name": "p95", "value": 1700, "unit": "ms", "threshold": 1000}],
        }))
        wait_task(client, perf_task, "performance")
        unwrap(client.get("/api/v1/performance/", params={"project_id": project_id}))
        results.append("performance")

        api_cases = unwrap(client.get("/api/v1/api-automation/cases", params={"project_id": project_id}))
        if api_cases:
            api_auto_task = unwrap(client.post("/api/v1/api-automation/execs", json={
                "project_id": project_id,
                "name": f"接口自动化 {stamp}",
                "case_ids": [api_cases[0]["id"]],
                "exec_param": {"base_url": BASE_URL},
            }))
            wait_task(client, api_auto_task, "api_automation")
        else:
            created = unwrap(client.post("/api/v1/agent-tasks/", json={
                "agent_key": "api_automation",
                "project_id": project_id,
                "input_payload": {"name": f"接口自动化 {stamp}", "case_ids": [], "exec_param": {"base_url": BASE_URL}},
            }))
            wait_task(client, created, "api_automation_empty")
        unwrap(client.get("/api/v1/api-automation/execs", params={"project_id": project_id}))
        results.append("api_automation")

        ui_cases = unwrap(client.get("/api/v1/ui-automation/cases", params={"project_id": project_id}))
        if ui_cases:
            ui_auto_task = unwrap(client.post("/api/v1/ui-automation/execs", json={
                "project_id": project_id,
                "name": f"UI自动化 {stamp}",
                "case_ids": [ui_cases[0]["id"]],
                "exec_param": {"base_url": "http://localhost:3000", "browser": "Chromium"},
            }))
            wait_task(client, ui_auto_task, "ui_automation")
        else:
            created = unwrap(client.post("/api/v1/agent-tasks/", json={
                "agent_key": "ui_automation",
                "project_id": project_id,
                "input_payload": {"name": f"UI自动化 {stamp}", "case_ids": [], "exec_param": {"base_url": "http://localhost:3000"}},
            }))
            wait_task(client, created, "ui_automation_empty")
        unwrap(client.get("/api/v1/ui-automation/execs", params={"project_id": project_id}))
        results.append("ui_automation")

        all_tasks = unwrap(client.get("/api/v1/agent-tasks/", params={"project_id": project_id}))
        if all_tasks["total"] < 1:
            raise SmokeFailure("agent task list did not include smoke tasks")
        results.append("agent_tasks")

    report = Path("smoke-real-services-report.txt")
    report.write_text("\n".join(f"PASS {item}" for item in results) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
