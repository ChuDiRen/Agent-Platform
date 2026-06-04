import re

from app.schemas.api_document import (
    ApiDocumentAnalysisRequest,
    ApiDocumentAnalysisResponse,
    ApiDocumentFinding,
)


def analyze_api_document(payload: ApiDocumentAnalysisRequest) -> ApiDocumentAnalysisResponse:
    content = payload.content
    findings: list[ApiDocumentFinding] = []

    checks = [
        (
            "missing-response-params",
            "缺少响应参数定义",
            "接口文档中未明确描述返回的响应参数，包括成功和失败场景下的响应结构、字段名称、类型及含义。"
            "这会影响测试用例对响应结果的校验设计。",
            "响应定义",
            "high",
            _has_response_details(content),
        ),
        (
            "missing-error-codes",
            "缺少错误码和异常场景说明",
            "接口文档未覆盖参数错误、权限不足、认证失败、服务异常等错误返回。"
            "建议补充错误码、错误消息格式和触发条件。",
            "异常场景",
            "high",
            _contains_any(content, ["错误码", "异常", "失败", "error", "code", "message"]),
        ),
        (
            "missing-field-constraints",
            "未定义字段长度和格式限制",
            "请求参数缺少必填、长度、格式、枚举范围或默认值说明。"
            "建议为每个参数补充约束，避免前后端和测试口径不一致。",
            "参数约束",
            "medium",
            _contains_any(content, ["必填", "长度", "格式", "枚举", "默认", "required", "max", "min"]),
        ),
        (
            "missing-auth",
            "缺少认证或会话机制说明",
            "文档未说明接口是否需要 token、cookie、签名或其他鉴权信息，也未说明鉴权失败的返回。"
            "建议补充认证方式、请求头字段和过期处理规则。",
            "安全规则",
            "medium",
            _contains_any(content, ["token", "cookie", "authorization", "鉴权", "认证", "登录态", "签名"]),
        ),
        (
            "missing-success-example",
            "未提供成功响应示例",
            "文档没有给出成功返回 JSON 示例，测试人员难以确认断言字段和业务状态。"
            "建议增加至少一个完整成功响应示例。",
            "示例完整性",
            "medium",
            _contains_any(content, ["成功示例", "响应示例", "返回示例", "response", "{", "}"]),
        ),
        (
            "missing-method-or-url",
            "请求方法或 URL 描述不完整",
            "接口文档需要同时明确请求 URL 和 HTTP 方法。建议补充完整请求路径、方法和环境说明。",
            "接口基础信息",
            "high",
            _has_method(content) and _has_url(content),
        ),
    ]

    for finding_id, title, description, category, severity, passed in checks:
        if not passed:
            findings.append(
                ApiDocumentFinding(
                    id=finding_id,
                    title=title,
                    description=description,
                    severity=severity,
                    category=category,
                )
            )

    if not findings:
        findings.append(
            ApiDocumentFinding(
                id="document-baseline-ok",
                title="接口基础信息较完整",
                description="当前接口文档已经覆盖请求地址、请求方式、参数与返回信息。建议继续补充边界值、兼容性和幂等性说明。",
                severity="low",
                category="质量建议",
            )
        )

    if payload.extra_prompt:
        findings.append(
            ApiDocumentFinding(
                id="extra-focus",
                title="已结合补充分析要求",
                description=f"补充要求：{payload.extra_prompt}",
                severity="low",
                category="补充要求",
            )
        )

    return ApiDocumentAnalysisResponse(
        document_id=payload.document_id,
        title=payload.title,
        findings=findings,
    )


def _contains_any(content: str, keywords: list[str]) -> bool:
    text = content.lower()
    return any(keyword.lower() in text for keyword in keywords)


def _has_method(content: str) -> bool:
    return bool(re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\b", content, re.IGNORECASE))


def _has_url(content: str) -> bool:
    return bool(re.search(r"(https?://|/api/|/v\d+/|请求\s*URL|接口地址)", content, re.IGNORECASE))


def _has_response_details(content: str) -> bool:
    return _contains_any(content, ["响应参数", "返回参数", "响应结构", "response"]) and _contains_any(
        content, ["字段", "类型", "说明", "datatype"]
    )
