import json
import re
import time

from app.schemas.test_case import TestCaseCreate, TestCaseGenerateRequest


def _extract_code_after(label: str, content: str, default: str) -> str:
    pattern = rf"{label}\s*\n+```(?:\w+)?\s*([\s\S]*?)```"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        if value:
            return value
    return default


def _extract_params(content: str) -> list[str]:
    params: list[str] = []
    for line in content.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"参数名", "---"}:
            continue
        if cells[0] and not cells[0].startswith("-"):
            params.append(cells[0])
    return params or ["userName", "password"]


def _request_steps(path: str, method: str, body: dict, headers: dict | None = None) -> str:
    return json.dumps(
        {
            "path": path,
            "method": method.upper(),
            "urlParams": {},
            "form": {},
            "json": body,
            "cookies": {},
            "headers": headers or {},
        },
        ensure_ascii=False,
    )


def generate_test_cases(payload: TestCaseGenerateRequest) -> tuple[list[TestCaseCreate], int]:
    started = time.perf_counter()
    title = payload.module.title.strip()
    content = payload.module.content.strip()
    extra = (payload.extra_requirement or "").strip()
    path = _extract_code_after("请求 URL", content, "/api/user/login")
    method = _extract_code_after("请求方式", content, "POST").splitlines()[0].strip().upper()
    params = _extract_params(content)
    account_key = next((item for item in params if item.lower() in {"username", "user_name", "account", "email"}), params[0])
    password_key = next((item for item in params if "password" in item.lower() or item in {"密码"}), params[-1])
    base_body = {account_key: f"{{{{{account_key}}}}}", password_key: "{{password}}"}
    if "remember" in content.lower():
        base_body["remember"] = False
    suffix = f"，并关注{extra}" if extra else ""

    cases = [
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name=f"验证使用正确的{account_key}和密码可成功调用接口",
            priority=1,
            precondition=f"系统中存在一个已注册账号，{account_key}为“{{{{{account_key}}}}}”，密码为“{{{{password}}}}”",
            steps=_request_steps(path, method, base_body),
            expected=f"返回状态码为200，响应体包含成功标识或有效登录凭据{suffix}",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name=f"验证使用错误的密码无法调用{title}接口",
            priority=1,
            precondition=f"系统中存在一个已注册账号，{account_key}为“{{{{{account_key}}}}}”",
            steps=_request_steps(path, method, {**base_body, password_key: "错误密码"}),
            expected="返回状态码为401或业务错误码，响应体包含账号或密码错误等有效提示信息",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name=f"验证不提供{account_key}时接口返回错误",
            priority=2,
            precondition="无",
            steps=_request_steps(path, method, {key: value for key, value in base_body.items() if key != account_key}),
            expected=f"返回状态码为400或业务错误码，响应体包含{account_key}不能为空等校验错误信息",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name=f"验证不提供{password_key}时接口返回错误",
            priority=2,
            precondition="无",
            steps=_request_steps(path, method, {key: value for key, value in base_body.items() if key != password_key}),
            expected=f"返回状态码为400或业务错误码，响应体包含{password_key}不能为空等校验错误信息",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name=f"验证{account_key}为空字符串时接口返回错误",
            priority=2,
            precondition="无",
            steps=_request_steps(path, method, {**base_body, account_key: ""}),
            expected=f"返回状态码为400或业务错误码，响应体包含{account_key}不能为空或格式错误提示",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name="验证SQL注入尝试经过接口被拒绝",
            priority=5,
            precondition="无",
            steps=_request_steps(path, method, {**base_body, account_key: "' OR '1'='1"}),
            expected="接口拒绝异常输入或按普通字符串处理，不返回登录成功状态，不泄露数据库错误信息",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name="验证缺少Content-Type请求头时接口处理符合预期",
            priority=3,
            precondition="无",
            steps=_request_steps(path, method, base_body, headers={}),
            expected="接口返回明确错误或仍可按后端约定解析请求，响应结果与接口规范一致",
        ),
        TestCaseCreate(
            project_id=payload.project_id,
            module_id=payload.module.id,
            name=f"验证{method}接口使用不支持的方法时返回错误",
            priority=4,
            precondition="无",
            steps=_request_steps(path, "GET" if method != "GET" else "POST", base_body),
            expected="接口返回405或业务错误码，不执行接口核心业务逻辑",
        ),
    ]
    elapsed_ms = max(1, int((time.perf_counter() - started) * 1000))
    return cases, elapsed_ms
