"""接口自动化脚本工具"""
from __future__ import annotations
import json
from langchain_core.tools import tool


@tool
def generate_api_script(
    method: str,
    path: str,
    body: str = "{}",
    headers: str = "{}",
    assertions: str = "[]",
) -> str:
    """生成单个接口的 pytest 测试脚本。

    Args:
        method: HTTP 方法 (GET/POST/PUT/DELETE)。
        path: 接口路径。
        body: 请求体 JSON 字符串。
        headers: 请求头 JSON 字符串。
        assertions: 断言规则 JSON 数组。
    """
    body_dict = json.loads(body) if body and body != "{}" else None
    headers_dict = json.loads(headers) if headers and headers != "{}" else {}

    script = f'''import pytest
import httpx

BASE_URL = "http://localhost:8000"


def test_{path.replace("/", "_").strip("_").lower()}():
    """测试 {method} {path}"""
    url = f"{{BASE_URL}}{path}"
    headers = {json.dumps(headers_dict, indent=8)}'''

    if body_dict:
        script += f'''
    payload = {json.dumps(body_dict, indent=8)}'''

    if method.upper() in ("POST", "PUT", "PATCH"):
        script += f'''
    response = httpx.{method.lower()}(url, json=payload, headers=headers, timeout=30)'''
    else:
        script += f'''
    response = httpx.{method.lower()}(url, headers=headers, timeout=30)'''

    script += '''
    # 断言
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.elapsed.total_seconds() < 3, f"Response too slow: {response.elapsed.total_seconds()}s"
    data = response.json()
    assert data is not None, "Response body should not be empty"
'''

    return json.dumps({"script": script, "path": path, "method": method}, ensure_ascii=False, indent=2)


@tool
def build_test_suite(cases: str) -> str:
    """将多个测试用例组装为完整的 pytest 测试套件。

    Args:
        cases: JSON 数组格式的测试用例列表。
    """
    case_list = json.loads(cases) if isinstance(cases, str) else cases
    suite = ['"""自动生成的接口测试套件"""', "import pytest", "import httpx", "", "BASE_URL = 'http://localhost:8000'", ""]
    for c in case_list[:10]:
        name = c.get("name", "test").replace(" ", "_")
        suite.append(f"def test_{name.lower()}():")
        suite.append(f'    """{c.get("name", "")}"""')
        suite.append(f"    # TODO: 实现测试逻辑")
        suite.append("")
    return json.dumps({"suite": "\n".join(suite), "total_cases": len(case_list)}, ensure_ascii=False, indent=2)


@tool
def generate_report_template(format: str = "markdown") -> str:
    """生成测试报告模板。

    Args:
        format: 报告格式 — markdown/html/json。
    """
    template = """# 接口自动化测试报告

## 概览
- 总用例数: {total}
- 通过: {passed}
- 失败: {failed}
- 跳过: {skipped}
- 执行时间: {duration}

## 详细结果

| # | 用例名 | 状态 | 耗时 | 备注 |
|---|--------|------|------|------|
"""
    return json.dumps({"format": format, "template": template}, ensure_ascii=False, indent=2)
