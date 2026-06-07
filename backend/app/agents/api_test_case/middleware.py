"""接口用例设计专用中间件 — 追踪用例设计覆盖度"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.api_test_case")


class ApiTestCaseMiddleware(AgentMiddleware):
    name = "api_test_case"

    def __init__(self):
        self._cases_designed = 0
        self._params_analyzed: set[str] = set()

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "design_api_cases":
                    self._cases_designed += 1
                elif name == "generate_param_combinations":
                    self._params_analyzed.add(str(tc.get("args", {}).get("params", ""))[:50])
        return response

    def get_summary(self) -> dict:
        return {"cases_designed": self._cases_designed, "params_analyzed": len(self._params_analyzed)}
