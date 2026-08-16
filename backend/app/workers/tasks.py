from __future__ import annotations

from app.db.session import SessionLocal
from app.models.agent_task import AgentTaskStatus
from app.services.agent_task_service import AgentTaskService, TERMINAL_STATUSES
from app.workers.celery_app import celery_app
from app.workers.executor import AgentExecutionContext, CancelledError
from app.workers.registry import get_executor


@celery_app.task(name="app.workers.tasks.run_agent_task")
def run_agent_task(task_id: int):
    db = SessionLocal()
    task = None
    service = None
    try:
        service = AgentTaskService(db)
        task = service.get_task(task_id)
        if task is None:
            return {"status": "missing"}
        if task.status == AgentTaskStatus.CANCELLED.value:
            return {"status": task.status}
        if task.status in TERMINAL_STATUSES:
            return {"status": task.status}

        # 幂等守卫：仅当任务仍处于 queued 时才允许进入 running；
        # 若已被其他 worker 抢先 start（running），本 worker 直接退出。
        if not service.try_start_task(task):
            return {"status": task.status}

        context = AgentExecutionContext(task.id, task.project_id, task.user_id, service)
        executor = get_executor(task.agent_key)
        result = executor(task.input_payload or {}, context)

        if context.is_cancelled():
            service.cancel_task(task)
            return {"status": AgentTaskStatus.CANCELLED.value}

        for artifact in result.artifacts:
            context.add_artifact(**artifact)

        service.succeed_task(
            task,
            {
                "summary": result.summary,
                "output": result.output,
                "artifacts": result.artifacts,
            },
        )
        return {"status": AgentTaskStatus.SUCCEEDED.value}
    except CancelledError:
        # 协作式取消：executor 主动中断，标记为 cancelled
        db.rollback()
        if service is not None:
            cancelled_task = service.get_task(task_id)
            if cancelled_task is not None and cancelled_task.status not in TERMINAL_STATUSES:
                service.cancel_task(cancelled_task)
        return {"status": AgentTaskStatus.CANCELLED.value}
    except Exception as exc:
        db.rollback()
        if service is not None:
            failed_task = service.get_task(task_id)
            if failed_task is not None and failed_task.status not in TERMINAL_STATUSES:
                service.fail_task(failed_task, str(exc))
        return {"status": AgentTaskStatus.FAILED.value, "error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.purge_old_agent_tasks")
def purge_old_agent_tasks(max_age_days: int = 30):
    """清理超过保留期的终态任务及其事件/产物。"""
    db = SessionLocal()
    try:
        service = AgentTaskService(db)
        purged = service.purge_old_tasks(max_age_days=max_age_days)
        return {"purged": purged}
    finally:
        db.close()
