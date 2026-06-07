"""AI 接口用例设计"""
from app.agents.base import BaseAgent
from app.agents.api_test_case.prompts import SYSTEM_PROMPT
from app.agents.api_test_case.tools import design_api_cases, generate_param_combinations, suggest_assertions
from app.agents.api_test_case.middleware import ApiTestCaseMiddleware


class ApiTestCaseAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [design_api_cases, generate_param_combinations, suggest_assertions]

    def _build_middleware(self):
        return [ApiTestCaseMiddleware()]


def create_api_test_case_agent(**kwargs):
    return ApiTestCaseAgent(**kwargs)
