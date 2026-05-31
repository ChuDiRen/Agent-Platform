import csv
import io
import json
import os
import time
from typing import Any

from fastapi import HTTPException

from app.schemas.test_data import TestDataField, TestDataGenerateRequest, TestDataGenerateResponse


def render_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _render_response(
    rows: list[dict[str, Any]], payload: TestDataGenerateRequest, started: float
) -> TestDataGenerateResponse:
    content = render_csv(rows) if payload.format == "csv" else json.dumps(
        {"data": rows}, ensure_ascii=False, indent=2
    )
    elapsed_ms = max(1, int((time.perf_counter() - started) * 1000))
    return TestDataGenerateResponse(
        data=rows,
        content=content,
        format=payload.format,
        count=payload.count,
        elapsed_ms=elapsed_ms,
    )


def _deepagents_rows(payload: TestDataGenerateRequest) -> list[dict[str, Any]]:
    model = os.getenv("DEEPAGENTS_MODEL")
    if not model:
        raise HTTPException(status_code=503, detail="DEEPAGENTS_MODEL is not configured")

    try:
        from deepagents import create_deep_agent
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="deepagents is not installed") from exc

    prompt = (
        "Generate strict JSON only. Return an array of objects matching these field definitions. "
        f"Language: {payload.lang}. Count: {payload.count}. Hint: {payload.hint or ''}. "
        f"Fields: {json.dumps([field.model_dump() for field in payload.fields], ensure_ascii=False)}"
    )

    agent = create_deep_agent(
        model=model,
        tools=[],
        system_prompt=(
            "You generate realistic QA test data. Return JSON only, with no markdown."
        ),
    )
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    messages = result.get("messages", []) if isinstance(result, dict) else []
    content = messages[-1].content if messages else ""
    rows = json.loads(content)

    if not isinstance(rows, list) or len(rows) != payload.count:
        raise HTTPException(status_code=502, detail="deepagents returned an invalid row count")
    field_names = {field.name for field in payload.fields}
    if not all(isinstance(row, dict) and field_names.issubset(row.keys()) for row in rows):
        raise HTTPException(status_code=502, detail="deepagents returned invalid fields")
    return rows


def generate_test_data_response(payload: TestDataGenerateRequest) -> TestDataGenerateResponse:
    started = time.perf_counter()
    rows = _deepagents_rows(payload)
    return _render_response(rows, payload, started)
