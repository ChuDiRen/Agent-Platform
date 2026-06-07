"""接口自动化专用中间件 — 追踪脚本生成统计"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.api_automation")


class ApiAutomationMiddleware(AgentMiddleware):
    name = "api_automation"

    def __init__(self):
        self._scripts_generated = 0
        self._suites_built = 0

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "generate_api_script":
                    self._scripts_generated += 1
                elif name == "build_test_suite":
                    self._suites_built += 1
        return response

    def get_summary(self) -> dict:
        return {"scripts_generated": self._scripts_generated, "suites_built": self._suites_built}
