"""真实服务链路测试。

这些用例不使用 TestClient 和 mock 服务，直接访问正在运行的前后端、Redis、Celery worker。
运行前置条件：
- 后端服务：http://localhost:8000
- 前端服务：http://localhost:3000
- Redis/Celery broker 可达
- Celery worker 已启动并消费同一 broker

默认不会在普通回归中执行，需显式设置 RUN_REAL_SERVICE_TESTS=1。
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest


pytestmark = pytest.mark.real_service
if os.getenv("RUN_REAL_SERVICE_TESTS") != "1":
    pytestmark = [
        pytest.mark.real_service,
        pytest.mark.skip(reason="真实服务测试需设置 RUN_REAL_SERVICE_TESTS=1 后显式运行"),
    ]

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

BACKEND_BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:3000"
TASK_TIMEOUT_SECONDS = 120


class RealServiceFailure(AssertionError):
    """真实服务链路断言失败。"""



def unwrap(response: httpx.Response) -> Any:
    try:
        body = response.json()
    except ValueError as exc:
        raise RealServiceFailure(f"{response.request.method} {response.request.url} returned non-JSON") from exc

    if response.status_code != 200:
        raise RealServiceFailure(f"{response.request.method} {response.request.url} HTTP {response.status_code}: {body}")
    if body.get("code") != 0:
        raise RealServiceFailure(f"{response.request.method} {response.request.url} API code {body.get('code')}: {body}")
    return body.get("data")


def wait_task(client: httpx.Client, task: dict[str, Any], label: str) -> dict[str, Any]:
    deadline = time.time() + TASK_TIMEOUT_SECONDS
    task_id = task["id"]

    while time.time() < deadline:
        current = unwrap(client.get(f"/api/v1/agent-tasks/{task_id}"))
        if current["status"] in {"succeeded", "failed", "cancelled"}:
            if current["status"] != "succeeded":
                raise RealServiceFailure(f"{label} task #{task_id} ended as {current['status']}: {current.get('error_message')}")
            unwrap(client.get(f"/api/v1/agent-tasks/{task_id}/events"))
            unwrap(client.get(f"/api/v1/agent-tasks/{task_id}/artifacts"))
            return current
        time.sleep(1)

    raise RealServiceFailure(f"{label} task #{task_id} timed out")


def authenticate_admin(client: httpx.Client) -> None:
    login = unwrap(client.post("/api/v1/users/login", json={"email": "admin@qq.com", "password": "admin123456"}))
    token = login["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})


def test_real_services_cover_core_business_and_agent_flows() -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    with httpx.Client(base_url=BACKEND_BASE_URL, timeout=15) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json().get("status") == "ok"

        authenticate_admin(client)

        project = unwrap(
            client.post(
                "/api/v1/projects/",
                json={
                    "name": f"真实服务项目 {stamp}",
                    "description": "真实服务 pytest 链路测试",
                },
            )
        )
        project_id = project["id"]
        unwrap(client.get(f"/api/v1/projects/{project_id}"))
        unwrap(client.put(f"/api/v1/projects/{project_id}", json={"description": "真实服务项目已更新"}))
        unwrap(client.get("/api/v1/projects/"))

        agents = unwrap(client.get("/api/v1/agents/"))
        assert agents, "Agent 目录不能为空"

        document = unwrap(
            client.post(
                "/api/v1/documents/",
                json={
                    "project_id": project_id,
                    "name": f"需求文档 {stamp}",
                    "title": "登录需求",
                    "content": "用户可以使用邮箱和密码登录，失败时提示错误原因。",
                    "is_directory": False,
                },
            )
        )
        review_task = unwrap(
            client.post(
                "/api/v1/documents/review",
                json={
                    "document_id": document["id"],
                    "title": document["title"],
                    "content": document["content"],
                },
            )
        )
        wait_task(client, review_task, "requirement_review")

        api_document = unwrap(
            client.post(
                "/api/v1/api-documents/",
                json={
                    "project_id": project_id,
                    "name": f"接口文档 {stamp}",
                    "title": "登录接口",
                    "content": "POST /api/v1/users/login request: email,password response: access_token",
                    "is_directory": False,
                },
            )
        )
        api_doc_task = unwrap(
            client.post(
                "/api/v1/api-documents/analysis",
                json={
                    "document_id": api_document["id"],
                    "title": api_document["title"],
                    "content": api_document["content"],
                },
            )
        )
        wait_task(client, api_doc_task, "api_document")

        template = unwrap(
            client.post(
                "/api/v1/test-data/templates/",
                json={
                    "project_id": project_id,
                    "name": f"用户数据模板 {stamp}",
                    "fields": [{"name": "email", "type": "email"}, {"name": "age", "type": "number"}],
                    "count": 2,
                    "format": "json",
                    "lang": "zh",
                },
            )
        )
        unwrap(client.get(f"/api/v1/test-data/templates/{template['id']}"))
        test_data_task = unwrap(
            client.post(
                "/api/v1/test-data/generate",
                json={
                    "fields": [{"name": "email", "type": "email"}, {"name": "age", "type": "number"}],
                    "count": 2,
                    "format": "json",
                    "lang": "zh",
                },
            )
        )
        wait_task(client, test_data_task, "test_data")

        test_case_task = unwrap(
            client.post(
                "/api/v1/test-cases/generate",
                json={
                    "project_id": project_id,
                    "module": {
                        "id": 101,
                        "title": "登录模块",
                        "content": "用户输入邮箱和密码后可以登录系统。",
                    },
                    "extra_requirement": "覆盖正确密码和错误密码",
                },
            )
        )
        wait_task(client, test_case_task, "test_case")
        saved_cases = unwrap(
            client.post(
                "/api/v1/test-cases/apply",
                json={
                    "cases": [
                        {
                            "project_id": project_id,
                            "module_id": 101,
                            "name": f"登录成功用例 {stamp}",
                            "priority": 1,
                            "precondition": "用户已注册",
                            "steps": "输入正确邮箱和密码，点击登录",
                            "expected": "登录成功",
                        }
                    ]
                },
            )
        )
        unwrap(client.get("/api/v1/test-cases/", params={"project_id": project_id}))
        unwrap(client.get(f"/api/v1/test-cases/{saved_cases[0]['id']}"))

        performance_task = unwrap(
            client.post(
                "/api/v1/performance/analyze",
                json={
                    "project_id": project_id,
                    "name": f"性能分析 {stamp}",
                    "scenario": "登录接口压测",
                    "raw_text": "avg 860ms, p95 1700ms, error 2.5%, throughput 180, CPU 76%",
                    "metrics": [{"name": "p95", "value": 1700, "unit": "ms", "threshold": 1000}],
                },
            )
        )
        wait_task(client, performance_task, "performance")
        unwrap(client.get("/api/v1/performance/", params={"project_id": project_id}))

        api_cases = unwrap(client.get("/api/v1/api-automation/cases", params={"project_id": project_id}))
        api_auto_task = unwrap(
            client.post(
                "/api/v1/agent-tasks/",
                json={
                    "agent_key": "api_automation",
                    "project_id": project_id,
                    "input_payload": {
                        "name": f"接口自动化 {stamp}",
                        "case_ids": [api_cases[0]["id"]] if api_cases else [],
                        "exec_param": {"base_url": BACKEND_BASE_URL},
                    },
                },
            )
        )
        wait_task(client, api_auto_task, "api_automation")
        unwrap(client.get("/api/v1/api-automation/execs", params={"project_id": project_id}))

        ui_cases = unwrap(client.get("/api/v1/ui-automation/cases", params={"project_id": project_id}))
        ui_auto_task = unwrap(
            client.post(
                "/api/v1/agent-tasks/",
                json={
                    "agent_key": "ui_automation",
                    "project_id": project_id,
                    "input_payload": {
                        "name": f"UI自动化 {stamp}",
                        "case_ids": [ui_cases[0]["id"]] if ui_cases else [],
                        "exec_param": {"base_url": FRONTEND_BASE_URL, "browser": "Chromium"},
                    },
                },
            )
        )
        wait_task(client, ui_auto_task, "ui_automation")
        unwrap(client.get("/api/v1/ui-automation/execs", params={"project_id": project_id}))

        all_tasks = unwrap(client.get("/api/v1/agent-tasks/", params={"project_id": project_id}))
        assert all_tasks["total"] >= 1


def test_real_redis_celery_broker_connectivity() -> None:
    redis = pytest.importorskip("redis")

    from app.core.config import settings

    for label, url in [("broker", settings.CELERY_BROKER_URL), ("result_backend", settings.CELERY_RESULT_BACKEND)]:
        client = redis.Redis.from_url(url, socket_connect_timeout=3, socket_timeout=3)
        assert client.ping() is True, label
        assert client.info("server").get("redis_version")


def test_real_celery_worker_executes_agent_task() -> None:
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "false"

    from app.db.base import Base
    from app.db.session import SessionLocal, engine
    from app.models.agent_task import AgentTaskStatus
    from app.services.agent_task_enqueue import create_and_enqueue_agent_task
    from app.services.agent_task_service import AgentTaskService

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        task = create_and_enqueue_agent_task(
            db,
            agent_key="test_data",
            input_payload={
                "count": 1,
                "format": "json",
                "fields": [{"name": "email", "type": "email"}],
            },
        )
        service = AgentTaskService(db)
        deadline = time.time() + 30
        while time.time() < deadline:
            db.expire_all()
            current = service.get_task(task.id)
            if current and current.status in {
                AgentTaskStatus.SUCCEEDED.value,
                AgentTaskStatus.FAILED.value,
                AgentTaskStatus.CANCELLED.value,
            }:
                assert current.status == AgentTaskStatus.SUCCEEDED.value, current.error_message
                assert current.result_payload
                return
            time.sleep(1)
        raise RealServiceFailure(f"task_id={task.id} status=timeout")
    finally:
        db.close()
        engine.dispose()