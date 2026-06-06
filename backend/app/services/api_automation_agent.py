from datetime import datetime, timezone
from typing import Any

from app.schemas.api_automation import (
    ApiAutomationCase,
    ApiExecutionDetails,
    ApiExecutionResult,
    ApiRequestDetails,
)


def _case(
    *,
    case_id: int,
    module_id: int,
    module_name: str,
    priority: int,
    name: str,
    path: str,
    method: str,
    body: dict[str, Any],
    expected: str,
) -> ApiAutomationCase:
    return ApiAutomationCase(
        id=case_id,
        project_id=1,
        module_id=module_id,
        module_name=module_name,
        exec_type="HTTP 请求",
        priority=priority,
        name=name,
        request=ApiRequestDetails(
            path=path,
            method=method,
            body_json=body,
            headers={"Content-Type": "application/json"} if method != "GET" else {},
        ),
        expected=expected,
        created_at=datetime(2026, 6, 6, 9, 0, tzinfo=timezone.utc),
    )


API_AUTOMATION_CASES: list[ApiAutomationCase] = []


def list_api_automation_cases(
    *,
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
) -> list[ApiAutomationCase]:
    cases = API_AUTOMATION_CASES
    if project_id is not None:
        cases = [item for item in cases if item.project_id == project_id]
    if name:
        cases = [item for item in cases if name.lower() in item.name.lower()]
    if priority is not None:
        cases = [item for item in cases if item.priority == priority]
    if module_id is not None:
        cases = [item for item in cases if item.module_id == module_id]
    if exec_type:
        cases = [item for item in cases if item.exec_type == exec_type]
    return cases


def get_api_automation_case(case_id: int) -> ApiAutomationCase | None:
    return next((item for item in API_AUTOMATION_CASES if item.id == case_id), None)


def build_execution_details(
    *,
    case_ids: list[int],
    exec_param: dict[str, Any],
) -> ApiExecutionDetails:
    base_url = str(exec_param.get("base_url") or "").rstrip("/")
    credential = exec_param.get("credential") or {}
    case_params = exec_param.get("case_params") or {}
    results: list[ApiExecutionResult] = []

    for index, case_id in enumerate(case_ids):
        case = get_api_automation_case(case_id)
        if not case:
            continue
        request = case.request.model_copy(deep=True)
        body = request.body_json.copy()
        merged_params = {
            "username": credential.get("username") or case_params.get(str(case_id), {}).get("username") or "",
            "password": credential.get("password") or case_params.get(str(case_id), {}).get("password") or "",
        }
        for key, value in list(body.items()):
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                body[key] = merged_params.get(value.strip("{} "), value)
        request.body_json = body

        failed = index == 0
        response_body = (
            {"code": 500, "message": "未知异常，请联系管理员", "data": None}
            if failed
            else {"code": 200, "message": "success", "data": {"traceId": f"AI-{case_id}", "url": f"{base_url}{request.path}"}}
        )
        results.append(
            ApiExecutionResult(
                case_id=case.id,
                case_name=case.name,
                status="测试失败" if failed else "测试成功",
                expected=case.expected,
                ai_record=(
                    "AI断言发现HTTP状态码为200，但业务code为500，不满足成功登录预期。"
                    if failed
                    else "AI断言通过：状态码、业务code和响应结构均符合预期。"
                ),
                response={
                    "status_code": 200,
                    "headers": {"content-type": "application/json;charset=UTF-8"},
                    "body": response_body,
                },
                request=request,
            )
        )

    passed = sum(1 for item in results if item.status == "测试成功")
    failed_count = sum(1 for item in results if item.status == "测试失败")
    return ApiExecutionDetails(summary={"success": passed, "failed": failed_count, "total": len(results)}, results=results)
