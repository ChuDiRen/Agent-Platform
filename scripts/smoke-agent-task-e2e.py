"""Run a real Redis/Celery worker smoke test for one agent task.

The script expects a Celery worker to be running with the same environment:

    celery -A app.workers.celery_app.celery_app worker --loglevel=info --pool=solo

It uses the configured DATABASE_URL so the API process, worker process, and this
script all observe the same task row.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


def _load_backend_env() -> None:
    env_path = BACKEND / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    _load_backend_env()
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "false"

    from app.db.base import Base  # noqa: WPS433
    from app.db.session import engine, SessionLocal  # noqa: WPS433
    from app.models.agent_task import AgentTaskStatus  # noqa: WPS433
    from app.services.agent_task_enqueue import create_and_enqueue_agent_task  # noqa: WPS433
    from app.services.agent_task_service import AgentTaskService  # noqa: WPS433

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
                print(f"task_id={current.id} status={current.status}")
                if current.error_message:
                    print(f"error={current.error_message}")
                if current.result_payload:
                    print(f"summary={current.result_payload.get('summary')}")
                return 0 if current.status == AgentTaskStatus.SUCCEEDED.value else 1
            time.sleep(1)
        print(f"task_id={task.id} status=timeout")
        return 1
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
