"""测试用例专用中间件 — 追踪用例生成统计"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.test_case")


class TestCaseMiddleware(AgentMiddleware):
    name = "test_case"

    def __init__(self):
        self._cases_generated = 0
        self._fields_analyzed: set[str] = set()

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "generate_cases_from_doc":
                    self._cases_generated += 1
                elif name == "analyze_boundary_values":
                    self._fields_analyzed.add(tc.get("args", {}).get("field_name", ""))
        return response

    def get_summary(self) -> dict:
        return {"cases_generated": self._cases_generated, "fields_analyzed": list(self._fields_analyzed)}
