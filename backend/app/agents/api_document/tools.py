"""接口文档分析工具"""
from __future__ import annotations
import json, re
from langchain_core.tools import tool


@tool
def extract_endpoints(content: str) -> str:
    """从接口文档中提取所有 API 端点。

    Args:
        content: 接口文档原文。
    """
    endpoints = []
    # 匹配 URL 模式
    url_pattern = r'(?:GET|POST|PUT|DELETE|PATCH|get|post|put|delete|patch)\s+([/\w\-{}.:]+)'
    urls = re.findall(url_pattern, content)
    # 匹配 method + path
    method_pattern = r'(?:请求方式|method)[：:\s]*(GET|POST|PUT|DELETE|PATCH)'
    methods = re.findall(method_pattern, content, re.IGNORECASE)

    for i, url in enumerate(urls[:20]):
        method = methods[i] if i < len(methods) else "GET"
        endpoints.append({"method": method.upper(), "path": url, "index": i})

    return json.dumps({"total": len(endpoints), "endpoints": endpoints}, ensure_ascii=False, indent=2)


@tool
def analyze_api_document(content: str) -> str:
    """分析接口文档，找出问题和改进建议。

    Args:
        content: 接口文档原文。
    """
    issues = []
    lower = content.lower()

    if "错误" not in lower and "error" not in lower and "异常" not in lower:
        issues.append({"severity": "high", "title": "缺少错误响应说明", "category": "完整性"})
    if "鉴权" not in lower and "authorization" not in lower and "token" not in lower:
        issues.append({"severity": "high", "title": "缺少鉴权说明", "category": "安全性"})
    if "频率" not in lower and "限流" not in lower and "rate" not in lower:
        issues.append({"severity": "medium", "title": "缺少频率限制说明", "category": "安全性"})
    if not re.search(r'状态码|status.?code|\d{3}', content):
        issues.append({"severity": "medium", "title": "缺少状态码定义", "category": "完整性"})

    return json.dumps({"issues": issues, "total": len(issues)}, ensure_ascii=False, indent=2)


@tool
def check_api_compliance(content: str) -> str:
    """检查接口文档是否符合 RESTful 规范。

    Args:
        content: 接口文档原文。
    """
    violations = []
    if re.search(r'get.*(?:add|create|insert)', content, re.IGNORECASE):
        violations.append({"rule": "RESTful", "detail": "GET 请求不应执行写操作"})
    if re.search(r'/api/\w+/\w+/\w+/\w+/\w+', content):
        violations.append({"rule": "URL层级", "detail": "URL 层级过深（超过4层），建议扁平化"})
    if "大驼峰" in content or re.search(r'[A-Z][a-z]+[A-Z]', content):
        violations.append({"rule": "命名", "detail": "字段名建议使用 snake_case 或 camelCase，不要混用"})

    return json.dumps({"violations": violations, "total": len(violations)}, ensure_ascii=False, indent=2)
