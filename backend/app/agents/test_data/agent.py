"""AI 测试数据生成"""
from app.agents.base import BaseAgent
from app.agents.test_data.prompts import SYSTEM_PROMPT
from app.agents.test_data.tools import generate_test_data, generate_boundary_data, convert_data_format
from app.agents.test_data.middleware import TestDataMiddleware


class TestDataAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [generate_test_data, generate_boundary_data, convert_data_format]

    def _build_middleware(self):
        return [TestDataMiddleware()]


def create_test_data_agent(**kwargs):
    return TestDataAgent(**kwargs)
