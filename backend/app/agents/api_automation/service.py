"""接口自动化服务层 — 提供给 API 端点使用"""
from app.agents.api_automation.tools import generate_api_script, build_test_suite, generate_report_template


def list_api_automation_cases():
    """返回可用的接口自动化用例列表。"""
    return []


def get_api_automation_case(case_id: int):
    """获取单个接口自动化用例。"""
    return None


def build_execution_details(case_id: int):
    """构建执行详情。"""
    return {}
