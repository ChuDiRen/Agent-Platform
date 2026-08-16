from __future__ import annotations

try:
    from celery import Celery
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    Celery = None

from app.core.config import settings


class _InlineTask:
    def __init__(self, fn):
        self.fn = fn

    def delay(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class _InlineCelery:
    def task(self, *args, **kwargs):
        def decorator(fn):
            return _InlineTask(fn)

        return decorator


if Celery is None:
    celery_app = _InlineCelery()
else:
    celery_app = Celery(
        "agent_platform",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=["app.workers.tasks"],
    )
    celery_app.conf.update(task_track_started=True)
    celery_app.conf.task_always_eager = settings.CELERY_TASK_ALWAYS_EAGER
    celery_app.conf.broker_connection_timeout = settings.CELERY_BROKER_CONNECTION_TIMEOUT
    celery_app.conf.broker_transport_options = {"socket_connect_timeout": 1, "socket_timeout": 1}
    # 任务可靠性：worker 丢失时拒绝并重试（默认最多 3 次，指数退避）
    celery_app.conf.task_acks_late = True
    celery_app.conf.task_reject_on_worker_lost = True
    celery_app.conf.task_acks_on_failure_or_timeout = False
    celery_app.conf.task_default_retry_delay = 10
    celery_app.conf.task_max_retries = 3

    # 定时清理终态任务（每天 04:00 执行，保留 30 天）
    celery_app.conf.beat_schedule = {
        "purge-old-agent-tasks-daily": {
            "task": "app.workers.tasks.purge_old_agent_tasks",
            "schedule": 24 * 60 * 60.0,
            "kwargs": {"max_age_days": 30},
        },
    }
