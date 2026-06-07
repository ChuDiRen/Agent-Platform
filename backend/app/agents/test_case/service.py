"""测试用例服务层 — 提供给 API 端点使用"""
from app.agents.test_case.tools import generate_cases_from_doc
from app.schemas.test_case import TestCaseCreate
import json, time


def generate_test_cases(payload):
    """根据需求文档生成测试用例。"""
    started = time.perf_counter()
    content = payload.module.content.strip() if hasattr(payload, "module") else str(payload)
    extra = (getattr(payload, "extra_requirement", "") or "").strip()

    result = generate_cases_from_doc.invoke({
        "content": content,
        "module_name": getattr(payload.module, "title", "") if hasattr(payload, "module") else "",
    })
    data = json.loads(result)

    cases = []
    for c in data.get("cases", []):
        cases.append(TestCaseCreate(
            project_id=getattr(payload, "project_id", None),
            module_id=getattr(payload.module, "id", None) if hasattr(payload, "module") else None,
            name=c.get("name", ""),
            priority=c.get("priority", 2),
            precondition=c.get("precondition", ""),
            steps=c.get("steps", ""),
            expected=c.get("expected", ""),
        ))

    elapsed_ms = max(1, int((time.perf_counter() - started) * 1000))
    return cases, elapsed_ms
