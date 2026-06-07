"""性能分析专用中间件 — 追踪瓶颈检测统计"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.performance")


class PerformanceMiddleware(AgentMiddleware):
    name = "performance"

    def __init__(self):
        self._analyses_run = 0
        self._bottlenecks_found = 0
        self._optimizations_suggested = 0

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "analyze_performance":
                    self._analyses_run += 1
                elif name == "detect_bottlenecks":
                    self._bottlenecks_found += 1
                elif name == "suggest_optimizations":
                    self._optimizations_suggested += 1
        return response

    def get_summary(self) -> dict:
        return {
            "analyses": self._analyses_run,
            "bottlenecks_detected": self._bottlenecks_found,
            "optimizations_suggested": self._optimizations_suggested,
        }
