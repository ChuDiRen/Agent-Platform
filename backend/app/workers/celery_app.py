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
