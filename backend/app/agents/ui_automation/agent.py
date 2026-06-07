"""AI UI 自动化"""
from app.agents.base import BaseAgent
from app.agents.ui_automation.prompts import SYSTEM_PROMPT
from app.agents.ui_automation.tools import generate_ui_script, analyze_page_elements, suggest_selectors
from app.agents.ui_automation.middleware import UiAutomationMiddleware


class UiAutomationAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [generate_ui_script, analyze_page_elements, suggest_selectors]

    def _build_middleware(self):
        return [UiAutomationMiddleware()]


def create_ui_automation_agent(**kwargs):
    return UiAutomationAgent(**kwargs)
