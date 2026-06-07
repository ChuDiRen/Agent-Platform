"""测试数据生成专用中间件 — 追踪数据生成统计"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.test_data")


class TestDataMiddleware(AgentMiddleware):
    name = "test_data"

    def __init__(self):
        self._data_batches = 0
        self._total_rows = 0
        self._formats_used: set[str] = set()

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "generate_test_data":
                    self._data_batches += 1
                elif name == "convert_data_format":
                    self._formats_used.add(tc.get("args", {}).get("target_format", "json"))
        return response

    def get_summary(self) -> dict:
        return {"data_batches": self._data_batches, "formats_used": list(self._formats_used)}
