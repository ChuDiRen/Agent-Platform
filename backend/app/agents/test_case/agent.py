"""AI 测试用例智能体"""
from app.agents.base import BaseAgent
from app.agents.test_case.prompts import SYSTEM_PROMPT, SUBAGENT_BOUNDARY, SUBAGENT_EDGE
from app.agents.test_case.tools import generate_cases_from_doc, analyze_boundary_values, suggest_edge_cases
from app.agents.test_case.middleware import TestCaseMiddleware


class TestCaseAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [generate_cases_from_doc, analyze_boundary_values, suggest_edge_cases]

    def _build_subagents(self):
        return [
            {"name": "boundary-analyzer", "description": "分析输入参数的边界值",
             "system_prompt": SUBAGENT_BOUNDARY, "tools": [analyze_boundary_values]},
            {"name": "edge-case-finder", "description": "发现异常和边界场景",
             "system_prompt": SUBAGENT_EDGE, "tools": [suggest_edge_cases]},
        ]

    def _build_middleware(self):
        return [TestCaseMiddleware()]


def create_test_case_agent(**kwargs):
    return TestCaseAgent(**kwargs)
