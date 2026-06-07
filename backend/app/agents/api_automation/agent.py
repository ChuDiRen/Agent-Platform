"""AI 接口自动化"""
from app.agents.base import BaseAgent
from app.agents.api_automation.prompts import SYSTEM_PROMPT
from app.agents.api_automation.tools import generate_api_script, build_test_suite, generate_report_template
from app.agents.api_automation.middleware import ApiAutomationMiddleware


class ApiAutomationAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [generate_api_script, build_test_suite, generate_report_template]

    def _build_middleware(self):
        return [ApiAutomationMiddleware()]


def create_api_automation_agent(**kwargs):
    return ApiAutomationAgent(**kwargs)
