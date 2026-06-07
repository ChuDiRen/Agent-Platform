"""接口文档分析专用中间件 — 追踪发现的问题统计"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.api_document")


class ApiDocumentMiddleware(AgentMiddleware):
    name = "api_document"

    def __init__(self):
        self._endpoints_found = 0
        self._issues_found = 0
        self._compliance_checks = 0

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "extract_endpoints":
                    self._endpoints_found += 1
                elif name == "analyze_api_document":
                    self._issues_found += 1
                elif name == "check_api_compliance":
                    self._compliance_checks += 1
        return response

    def get_summary(self) -> dict:
        return {
            "endpoint_extractions": self._endpoints_found,
            "issue_analyses": self._issues_found,
            "compliance_checks": self._compliance_checks,
        }
