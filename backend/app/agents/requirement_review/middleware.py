"""需求评估专用中间件 — 追踪评估维度和工具调用序列"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.requirement_review")


class RequirementReviewMiddleware(AgentMiddleware):
    name = "requirement_review"

    def __init__(self):
        self._dimensions: set[str] = set()
        self._tool_seq: list[str] = []

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                self._tool_seq.append(name)
                if name == "check_completeness":
                    self._dimensions.add(tc.get("args", {}).get("aspect", "all"))
        return response

    def get_summary(self) -> dict:
        return {"dimensions": list(self._dimensions), "tool_sequence": self._tool_seq}
