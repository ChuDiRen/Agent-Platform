"""接口自动化服务层 — 真实实现（基于 api_automation_cases 表 + 真实 HTTP 执行）。"""
from __future__ import annotations

import json
from typing import Any, Callable

import httpx

from app.schemas.api_automation import (
    ApiExecutionDetails,
    ApiExecutionResult,
    ApiRequestDetails,
)


def _case_to_request(case) -> dict[str, Any]:
    """从用例记录解析请求详情。"""
    raw = json.loads(case.request or "{}") if isinstance(case.request, str) else (case.request or {})
    return raw


def list_api_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    """返回接口自动化用例列表（来自 api_automation_cases 表）。"""
    from app.crud.api_automation_case import api_automation_case as case_crud

    return case_crud.get_multi_filtered(
        db=None,  # 端点层通过 get_db 注入；此函数由端点改为直接查询
        project_id=project_id,
        name=name,
        priority=priority,
        module_id=module_id,
        exec_type=exec_type,
    )


def get_api_automation_case(case_id: int):
    """获取单个接口自动化用例。"""
    from app.crud.api_automation_case import api_automation_case as case_crud

    return case_crud.get(None, case_id)


def build_execution_details(
    case_ids: list[int] | None = None,
    exec_param: dict | None = None,
    db=None,
    check_cancelled: Callable[[], None] | None = None,
) -> ApiExecutionDetails:
    """真实执行接口自动化：逐个用例发起 HTTP 请求并记录结果。

    check_cancelled: 可选取消检查点回调，供任务系统协作式取消。
    """
    from app.crud.api_automation_case import api_automation_case as case_crud

    exec_param = exec_param or {}
    base_url = (exec_param.get("base_url") or "").rstrip("/")
    ids = case_ids or []
    results: list[ApiExecutionResult] = []
    success = 0
    failed = 0

    for case_id in ids:
        if check_cancelled is not None:
            check_cancelled()
        case = case_crud.get(db, case_id) if db else None
        if case is None:
            failed += 1
            results.append(ApiExecutionResult(
                case_id=case_id,
                case_name=f"用例#{case_id}",
                status="failed",
                expected="",
                ai_record="用例不存在",
                response={"error": "用例不存在"},
                request=ApiRequestDetails(path="/", method="GET"),
            ))
            continue

        request = _case_to_request(case)
        method = (request.get("method") or "GET").upper()
        path = request.get("path") or "/"
        url = f"{base_url}{path}" if base_url else path
        headers = request.get("headers") or {}
        cookies = request.get("cookies") or {}
        json_body = request.get("json") or request.get("body_json")
        form = request.get("form") or {}
        params = request.get("url_params") or {}

        try:
            resp = httpx.request(
                method=method,
                url=url,
                headers=headers or None,
                cookies=cookies or None,
                params=params or None,
                json=json_body or None,
                data=form or None,
                timeout=30.0,
            )
            body = resp.text[:4000]
            ok = 200 <= resp.status_code < 400
            if ok:
                success += 1
            else:
                failed += 1
            results.append(ApiExecutionResult(
                case_id=case.id,
                case_name=case.name,
                status="passed" if ok else "failed",
                expected=case.expected or "",
                ai_record="",
                response={
                    "status_code": resp.status_code,
                    "headers": dict(resp.headers),
                    "body": body,
                },
                request=ApiRequestDetails(**request),
            ))
        except Exception as exc:
            failed += 1
            results.append(ApiExecutionResult(
                case_id=case.id,
                case_name=case.name,
                status="failed",
                expected=case.expected or "",
                ai_record=str(exc),
                response={"error": str(exc)},
                request=ApiRequestDetails(**request),
            ))

    return ApiExecutionDetails(
        summary={"success": success, "failed": failed, "total": len(ids)},
        results=results,
    )
