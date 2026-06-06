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


API_AUTOMATION_CASES: list[ApiAutomationCase] = [
    _case(
        case_id=10001,
        module_id=4101,
        module_name="用户登录",
        priority=1,
        name="验证用户使用正确手机号和密码登录",
        path="/user/login",
        method="POST",
        body={"username": "{{username}}", "password": "{{password}}"},
        expected="HTTP状态码为200，业务code为200，返回登录用户信息或token。",
    ),
    _case(
        case_id=10002,
        module_id=4101,
        module_name="用户登录",
        priority=1,
        name="验证用户密码错误时登录失败",
        path="/user/login",
        method="POST",
        body={"username": "{{username}}", "password": "wrong-password"},
        expected="HTTP状态码为200或401，业务响应提示账号或密码错误，不返回登录凭据。",
    ),
    _case(
        case_id=10003,
        module_id=4101,
        module_name="用户登录",
        priority=2,
        name="验证登录接口缺少用户名时返回参数校验错误",
        path="/user/login",
        method="POST",
        body={"password": "{{password}}"},
        expected="响应体包含用户名不能为空或参数校验失败提示。",
    ),
    _case(
        case_id=10004,
        module_id=4102,
        module_name="小说搜索",
        priority=2,
        name="验证按关键词搜索小说列表",
        path="/book/search",
        method="GET",
        body={},
        expected="HTTP状态码为200，返回包含keyword匹配结果的列表。",
    ),
    _case(
        case_id=10005,
        module_id=4103,
        module_name="章节详情",
        priority=3,
        name="验证获取小说章节详情",
        path="/chapter/detail",
        method="GET",
        body={},
        expected="HTTP状态码为200，返回章节标题、正文和下一章信息。",
    ),
]


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
    base_url = str(exec_param.get("base_url") or "http://novel.hctestedu.com").rstrip("/")
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
            "username": credential.get("username") or case_params.get(str(case_id), {}).get("username") or "18511114444",
            "password": credential.get("password") or case_params.get(str(case_id), {}).get("password") or "123456",
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
