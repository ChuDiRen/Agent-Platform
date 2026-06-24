"""UI 自动化服务层 — 提供给 API 端点使用"""
from app.agents.ui_automation.tools import generate_ui_script, analyze_page_elements, suggest_selectors


def list_ui_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    """返回可用的 UI 自动化用例列表。"""
    return []


def get_ui_automation_case(case_id: int):
    """获取单个 UI 自动化用例。"""
    return None


def build_ui_execution_details(case_id: int | None = None, case_ids: list[int] | None = None, exec_param: dict | None = None):
    """构建 UI 执行详情。"""
    ids = case_ids or ([case_id] if case_id is not None else [])
    return {
        "summary": {"success": len(ids), "failed": 0, "total": len(ids)},
        "results": [],
    }
