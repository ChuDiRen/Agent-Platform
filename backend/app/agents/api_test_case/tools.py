"""接口用例设计工具"""
from __future__ import annotations
import json
from langchain_core.tools import tool


@tool
def design_api_cases(content: str, focus: str = "all") -> str:
    """根据接口文档设计接口测试用例。

    Args:
        content: 接口文档内容（含 URL、Method、参数、响应）。
        focus: 关注点 — all(全部)/happy-path(正向)/error-handling(异常)/security(安全)。
    """
    cases = []
    idx = 1

    if focus in ("all", "happy-path"):
        cases.append({"id": f"API-{idx:03d}", "name": "正常请求返回预期响应", "priority": 1, "type": "happy-path"})
        cases.append({"id": f"API-{idx+1:03d}", "name": "可选参数不传时返回默认值", "priority": 2, "type": "happy-path"})
        idx += 2

    if focus in ("all", "error-handling"):
        cases.append({"id": f"API-{idx:03d}", "name": "缺少必选参数返回 400", "priority": 1, "type": "error"})
        cases.append({"id": f"API-{idx+1:03d}", "name": "参数类型错误返回 400", "priority": 2, "type": "error"})
        cases.append({"id": f"API-{idx+2:03d}", "name": "资源不存在返回 404", "priority": 2, "type": "error"})
        idx += 3

    if focus in ("all", "security"):
        cases.append({"id": f"API-{idx:03d}", "name": "无 Token 访问返回 401", "priority": 1, "type": "security"})
        cases.append({"id": f"API-{idx+1:03d}", "name": "越权访问返回 403", "priority": 1, "type": "security"})
        idx += 2

    return json.dumps({"cases": cases, "total": len(cases)}, ensure_ascii=False, indent=2)


@tool
def generate_param_combinations(params: str) -> str:
    """为接口参数生成组合测试数据。

    Args:
        params: JSON 格式的参数定义，如 '[{"name":"username","type":"string","required":true,"constraints":"6-20位"}]'。
    """
    param_list = json.loads(params) if isinstance(params, str) else params
    combos = []
    for p in param_list:
        name = p.get("name", "")
        ptype = p.get("type", "string")
        combo = {"param": name, "normal": [], "boundary": [], "invalid": []}
        if ptype == "string":
            combo["normal"] = ["valid_string"]
            combo["boundary"] = ["", "a" * 255]
            combo["invalid"] = [None, 123]
        elif ptype == "number":
            combo["normal"] = [1, 100]
            combo["boundary"] = [0, -1, 999999999]
            combo["invalid"] = ["abc", None]
        combos.append(combo)
    return json.dumps({"combinations": combos}, ensure_ascii=False, indent=2)


@tool
def suggest_assertions(response_example: str, status_code: int = 200) -> str:
    """根据响应示例建议断言规则。

    Args:
        response_example: 响应体示例 (JSON 字符串)。
        status_code: 预期状态码。
    """
    try:
        data = json.loads(response_example)
    except (json.JSONDecodeError, TypeError):
        data = {}

    assertions = [
        {"field": "status_code", "operator": "equals", "expected": status_code},
        {"field": "response_time", "operator": "less_than", "expected": "3000ms"},
    ]
    for key in (data.keys() if isinstance(data, dict) else []):
        assertions.append({"field": f"$.{key}", "operator": "exists"})

    return json.dumps({"assertions": assertions, "total": len(assertions)}, ensure_ascii=False, indent=2)
