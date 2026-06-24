"""Distributed agent task API and worker contract tests."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from app.models.agent_task import AgentTask, AgentTaskStatus


def test_create_agent_task_persists_and_enqueues(client, monkeypatch):
    delay = Mock()
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", delay)

    response = client.post(
        "/api/v1/agent-tasks/",
        json={
            "agent_key": "test_data",
            "project_id": 1,
            "input_payload": {"count": 2, "fields": [{"name": "email", "type": "email"}]},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["agent_key"] == "test_data"
    assert body["data"]["status"] == AgentTaskStatus.QUEUED
    delay.assert_called_once_with(body["data"]["id"])


def test_get_agent_task_events_and_artifacts(client, db, monkeypatch):
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", Mock())
    created = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "test_data", "input_payload": {"count": 1}},
    ).json()["data"]

    from app.services.agent_task_service import AgentTaskService

    service = AgentTaskService(db)
    service.emit_event(created["id"], event_type="progress", message="running", progress=50)
    service.add_artifact(
        created["id"],
        name="result.json",
        artifact_type="json",
        storage_path="/output/result.json",
        mime_type="application/json",
    )

    events = client.get(f"/api/v1/agent-tasks/{created['id']}/events").json()["data"]
    artifacts = client.get(f"/api/v1/agent-tasks/{created['id']}/artifacts").json()["data"]

    assert any(event["message"] == "running" and event["progress"] == 50 for event in events)
    assert artifacts[0]["name"] == "result.json"


def test_list_agent_tasks_supports_status_and_agent_filters(client, db, monkeypatch):
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", Mock())
    first = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "test_data", "input_payload": {"count": 1}},
    ).json()["data"]
    second = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "requirement_review", "input_payload": {"content": "需求"}},
    ).json()["data"]

    task = db.get(AgentTask, second["id"])
    task.status = AgentTaskStatus.FAILED
    db.commit()

    all_tasks = client.get("/api/v1/agent-tasks/").json()["data"]["items"]
    failed_tasks = client.get("/api/v1/agent-tasks/", params={"status": "failed"}).json()["data"]["items"]
    test_data_tasks = client.get("/api/v1/agent-tasks/", params={"agent_key": "test_data"}).json()["data"]["items"]

    assert [item["id"] for item in all_tasks] == [second["id"], first["id"]]
    assert [item["id"] for item in failed_tasks] == [second["id"]]
    assert [item["id"] for item in test_data_tasks] == [first["id"]]


def test_cancel_queued_agent_task_prevents_worker_execution(client, db, monkeypatch):
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", Mock())
    created = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "test_data", "input_payload": {"count": 1}},
    ).json()["data"]

    cancel_response = client.post(f"/api/v1/agent-tasks/{created['id']}/cancel")

    assert cancel_response.status_code == 200
    assert cancel_response.json()["data"]["status"] == AgentTaskStatus.CANCELLED

    from app.workers.tasks import run_agent_task

    run_agent_task.run(created["id"])
    db.expire_all()
    task = db.get(AgentTask, created["id"])
    assert task.status == AgentTaskStatus.CANCELLED
    assert task.result_payload is None


def test_cancel_completed_agent_task_is_rejected(client, db, monkeypatch):
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", Mock())
    created = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "test_data", "input_payload": {"count": 1}},
    ).json()["data"]

    task = db.get(AgentTask, created["id"])
    task.status = AgentTaskStatus.SUCCEEDED
    task.result_payload = {"summary": "done", "output": {"content": "ok"}}
    db.commit()

    response = client.post(f"/api/v1/agent-tasks/{created['id']}/cancel")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 400
    db.expire_all()
    unchanged = db.get(AgentTask, created["id"])
    assert unchanged.status == AgentTaskStatus.SUCCEEDED
    assert unchanged.result_payload["output"] == {"content": "ok"}


def test_retry_failed_agent_task_requeues(client, db, monkeypatch):
    delay = Mock()
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", delay)
    created = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "test_data", "input_payload": {"count": 1}},
    ).json()["data"]

    task = db.get(AgentTask, created["id"])
    task.status = AgentTaskStatus.FAILED
    task.error_message = "boom"
    db.commit()

    response = client.post(f"/api/v1/agent-tasks/{created['id']}/retry")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["status"] == AgentTaskStatus.QUEUED
    assert body["retry_count"] == 1
    delay.assert_called_with(created["id"])


def test_retry_non_failed_agent_task_does_not_enqueue(client, db, monkeypatch):
    delay = Mock()
    monkeypatch.setattr("app.services.agent_task_enqueue.run_agent_task.delay", delay)
    created = client.post(
        "/api/v1/agent-tasks/",
        json={"agent_key": "test_data", "input_payload": {"count": 1}},
    ).json()["data"]
    delay.reset_mock()

    response = client.post(f"/api/v1/agent-tasks/{created['id']}/retry")

    assert response.status_code == 200
    assert response.json()["code"] == 400
    delay.assert_not_called()


def test_worker_routes_task_to_executor_and_marks_success(db, monkeypatch):
    from app.services.agent_task_service import AgentTaskService
    from app.workers.executor import AgentExecutionResult
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(agent_key="test_data", input_payload={"count": 1})

    def fake_execute(payload, context):
        context.emit_event("halfway", progress=50)
        return AgentExecutionResult(summary="done", output={"content": "ok"})

    monkeypatch.setattr("app.workers.tasks.get_executor", lambda agent_key: fake_execute)
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    completed = db.get(AgentTask, task.id)
    assert completed.status == AgentTaskStatus.SUCCEEDED
    assert completed.result_payload["summary"] == "done"
    assert completed.result_payload["output"] == {"content": "ok"}


def test_worker_honors_cancellation_from_another_session(db, SessionLocal, monkeypatch):
    from app.services.agent_task_service import AgentTaskService
    from app.workers.executor import AgentExecutionResult
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(agent_key="test_data", input_payload={"count": 1})

    def fake_execute(payload, context):
        other_db = SessionLocal()
        try:
            other_service = AgentTaskService(other_db)
            other_task = other_service.get_task(context.task_id)
            other_service.cancel_task(other_task)
        finally:
            other_db.close()
        return AgentExecutionResult(summary="done", output={"content": "should-not-persist"})

    monkeypatch.setattr("app.workers.tasks.get_executor", lambda agent_key: fake_execute)
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    cancelled = db.get(AgentTask, task.id)
    assert cancelled.status == AgentTaskStatus.CANCELLED
    assert cancelled.result_payload is None


def test_worker_marks_task_failed_when_executor_raises(db, monkeypatch):
    from app.services.agent_task_service import AgentTaskService
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(agent_key="test_data", input_payload={"count": 1})

    def fake_execute(payload, context):
        raise RuntimeError("executor exploded")

    monkeypatch.setattr("app.workers.tasks.get_executor", lambda agent_key: fake_execute)
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    failed = db.get(AgentTask, task.id)
    assert failed.status == AgentTaskStatus.FAILED
    assert "executor exploded" in failed.error_message


def test_worker_json_encodes_pydantic_executor_output(db, monkeypatch):
    from app.schemas.test_case import TestCaseCreate
    from app.services.agent_task_service import AgentTaskService
    from app.workers.executor import AgentExecutionResult
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(agent_key="test_case", input_payload={"count": 1})

    def fake_execute(payload, context):
        return AgentExecutionResult(
            summary="done",
            output={
                "cases": [
                    TestCaseCreate(
                        name="登录成功",
                        precondition="存在有效账号",
                        steps="输入账号密码并提交",
                        expected="进入首页",
                    )
                ]
            },
        )

    monkeypatch.setattr("app.workers.tasks.get_executor", lambda agent_key: fake_execute)
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    completed = db.get(AgentTask, task.id)
    assert completed.status == AgentTaskStatus.SUCCEEDED
    assert completed.result_payload["output"]["cases"][0]["name"] == "登录成功"


def test_worker_rolls_back_and_marks_failed_when_success_commit_fails(db, monkeypatch):
    from app.services.agent_task_service import AgentTaskService
    from app.workers.executor import AgentExecutionResult
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(agent_key="test_data", input_payload={"count": 1})

    def fake_execute(payload, context):
        return AgentExecutionResult(summary="done", output={"content": object()})

    monkeypatch.setattr("app.workers.tasks.get_executor", lambda agent_key: fake_execute)
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    failed = db.get(AgentTask, task.id)
    assert failed.status == AgentTaskStatus.FAILED
    assert failed.error_message


def test_worker_persists_api_automation_record(db, monkeypatch):
    from app.models.api_test_cases_exec import ApiTestCasesExec
    from app.services.agent_task_service import AgentTaskService
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(
        agent_key="api_automation",
        project_id=9,
        input_payload={
            "name": "接口自动化任务",
            "exec_type": "HTTP 请求",
            "case_ids": [1, 2],
            "exec_param": {"base_url": "https://example.test"},
        },
    )
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    record = db.query(ApiTestCasesExec).one()
    completed = db.get(AgentTask, task.id)
    assert record.project_id == 9
    assert record.name == "接口自动化任务"
    assert completed.status == AgentTaskStatus.SUCCEEDED
    assert completed.result_payload["output"]["record_id"] == record.id


def test_worker_allows_empty_api_automation_without_record(db, monkeypatch):
    from app.models.api_test_cases_exec import ApiTestCasesExec
    from app.services.agent_task_service import AgentTaskService
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(
        agent_key="api_automation",
        project_id=9,
        input_payload={
            "name": "空接口自动化任务",
            "case_ids": [],
            "exec_param": {"base_url": "https://example.test"},
        },
    )
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    completed = db.get(AgentTask, task.id)
    assert db.query(ApiTestCasesExec).count() == 0
    assert completed.status == AgentTaskStatus.SUCCEEDED
    assert completed.result_payload["output"]["record_id"] is None
    assert completed.result_payload["output"]["details"]["summary"]["total"] == 0


def test_worker_persists_ui_automation_record(db, monkeypatch):
    from app.models.ui_test_cases_exec import UiTestCasesExec
    from app.services.agent_task_service import AgentTaskService
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(
        agent_key="ui_automation",
        project_id=10,
        input_payload={
            "name": "UI自动化任务",
            "exec_type": "WEB 网页",
            "case_ids": [1],
            "exec_param": {"browser": "Chromium"},
        },
    )
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    record = db.query(UiTestCasesExec).one()
    completed = db.get(AgentTask, task.id)
    assert record.project_id == 10
    assert record.name == "UI自动化任务"
    assert completed.status == AgentTaskStatus.SUCCEEDED
    assert completed.result_payload["output"]["record_id"] == record.id


def test_worker_allows_empty_ui_automation_without_record(db, monkeypatch):
    from app.models.ui_test_cases_exec import UiTestCasesExec
    from app.services.agent_task_service import AgentTaskService
    from app.workers.tasks import run_agent_task

    service = AgentTaskService(db)
    task = service.create_task(
        agent_key="ui_automation",
        project_id=10,
        input_payload={
            "name": "空UI自动化任务",
            "case_ids": [],
            "exec_param": {"base_url": "http://localhost:3000"},
        },
    )
    monkeypatch.setattr("app.workers.tasks.SessionLocal", lambda: db)

    run_agent_task.run(task.id)

    db.expire_all()
    completed = db.get(AgentTask, task.id)
    assert db.query(UiTestCasesExec).count() == 0
    assert completed.status == AgentTaskStatus.SUCCEEDED
    assert completed.result_payload["output"]["record_id"] is None
    assert completed.result_payload["output"]["details"]["summary"]["total"] == 0
