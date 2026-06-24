"""Verify Redis/Celery broker connectivity for distributed Agent tasks."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    backend = repo / "backend"
    sys.path.insert(0, str(backend))
    load_env(backend / ".env")

    from app.core.config import settings

    broker_url = settings.CELERY_BROKER_URL
    result_url = settings.CELERY_RESULT_BACKEND

    try:
        import redis
    except ImportError:
        print("ERROR: redis package is not installed. Run: pip install -r backend/requirements.txt")
        return 1

    for label, url in [("broker", broker_url), ("result_backend", result_url)]:
        client = redis.Redis.from_url(url, socket_connect_timeout=3, socket_timeout=3)
        pong = client.ping()
        info = client.info("server")
        dbsize = client.dbsize()
        print(f"{label}: ping={pong} redis_version={info.get('redis_version')} dbsize={dbsize}")

    print("Redis/Celery broker connectivity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
