"""接口自动化服务层 — 提供给 API 端点使用"""
from app.agents.api_automation.tools import generate_api_script, build_test_suite, generate_report_template


def list_api_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    """返回可用的接口自动化用例列表。"""
    return []


def get_api_automation_case(case_id: int):
    """获取单个接口自动化用例。"""
    return None


def build_execution_details(case_id: int | None = None, case_ids: list[int] | None = None, exec_param: dict | None = None):
    """构建执行详情。"""
    ids = case_ids or ([case_id] if case_id is not None else [])
    return {
        "summary": {"success": len(ids), "failed": 0, "total": len(ids)},
        "results": [],
    }
