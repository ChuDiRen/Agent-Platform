"""AI 接口文档分析"""
from app.agents.base import BaseAgent
from app.agents.api_document.prompts import SYSTEM_PROMPT
from app.agents.api_document.tools import analyze_api_document, check_api_compliance, extract_endpoints
from app.agents.api_document.middleware import ApiDocumentMiddleware


class ApiDocumentAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [analyze_api_document, check_api_compliance, extract_endpoints]

    def _build_middleware(self):
        return [ApiDocumentMiddleware()]


def create_api_document_agent(**kwargs):
    return ApiDocumentAgent(**kwargs)
