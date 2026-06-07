"""UI 自动化专用中间件 — 追踪页面分析和脚本生成"""

from __future__ import annotations
import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.ui_automation")


class UiAutomationMiddleware(AgentMiddleware):
    name = "ui_automation"

    def __init__(self):
        self._pages_analyzed = 0
        self._scripts_generated = 0
        self._selectors_suggested = 0

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        response = next_call(request)
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                name = tc.get("name", "")
                if name == "analyze_page_elements":
                    self._pages_analyzed += 1
                elif name == "generate_ui_script":
                    self._scripts_generated += 1
                elif name == "suggest_selectors":
                    self._selectors_suggested += 1
        return response

    def get_summary(self) -> dict:
        return {
            "pages_analyzed": self._pages_analyzed,
            "scripts_generated": self._scripts_generated,
            "selectors_suggested": self._selectors_suggested,
        }
