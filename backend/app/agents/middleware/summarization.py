"""Auto-summarization middleware for long conversations."""

from __future__ import annotations

import logging
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse

logger = logging.getLogger("agents.middleware.summarization")


def _estimate_tokens(text: str) -> int:
    """Estimate token count (CN ~1.5 char/token, EN ~4 char/token)."""
    cn = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    other = len(text) - cn
    return int(cn / 1.5 + other / 4)


def _estimate_messages_tokens(messages: list) -> int:
    total = 0
    for msg in messages:
        content = ""
        if hasattr(msg, "content"):
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
        total += _estimate_tokens(content)
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                total += _estimate_tokens(str(tc.get("args", {})))
    return total


class SummarizationMiddleware(AgentMiddleware):
    """Auto-compress old messages when token count exceeds threshold."""

    name = "summarization"

    def __init__(
        self,
        trigger_tokens: int = 8000,
        keep_recent: int = 6,
        compress_ratio: float = 0.3,
    ):
        self._trigger_tokens = trigger_tokens
        self._keep_recent = keep_recent
        self._compress_ratio = compress_ratio
        self._compress_count = 0
        self._total_tokens_saved = 0

    def wrap_model_call(self, request: ModelRequest, next_call) -> ModelResponse:
        messages = request.messages
        if not messages:
            return next_call(request)

        total = _estimate_messages_tokens(messages)

        if total <= self._trigger_tokens:
            return next_call(request)

        logger.info(f"[Summarization] tokens={total} > {self._trigger_tokens}, compressing...")

        try:
            self._compress_messages(messages, next_call)
            self._compress_count += 1
            new_total = _estimate_messages_tokens(messages)
            saved = total - new_total
            self._total_tokens_saved += max(0, saved)
            logger.info(f"[Summarization] done: {total} -> {new_total}, saved {saved}")
        except Exception as e:
            logger.warning(f"[Summarization] failed: {e}")

        return next_call(request)

    def _compress_messages(self, messages: list, next_call):
        if len(messages) <= self._keep_recent:
            return

        split_idx = len(messages) - self._keep_recent
        old_messages = messages[:split_idx]
        recent_messages = messages[split_idx:]

        old_text_parts = []
        for msg in old_messages:
            role = type(msg).__name__.replace("Message", "").lower()
            content = ""
            if hasattr(msg, "content"):
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if content.strip():
                old_text_parts.append(f"[{role}]: {content[:500]}")

        if not old_text_parts:
            return

        old_text = "\n".join(old_text_parts)
        target_pct = int(self._compress_ratio * 100)

        summary_prompt = (
            f"Please compress the following conversation history into a brief summary. "
            f"Keep key information and context. Target: {target_pct}% of original.\n\n"
            f"## History\n{old_text}\n\n"
            f"Output only the summary."
        )

        from langchain_core.messages import HumanMessage, SystemMessage
        summary_messages = [
            SystemMessage(content="You are a conversation summarizer."),
            HumanMessage(content=summary_prompt),
        ]

        try:
            resp = next_call(ModelRequest(messages=summary_messages))
            summary_text = resp.content if hasattr(resp, "content") else str(resp)
        except Exception:
            summary_text = old_text[:int(len(old_text) * self._compress_ratio)]

        from langchain_core.messages import SystemMessage
        summary_msg = SystemMessage(content=f"[Conversation Summary]\n{summary_text}")

        messages.clear()
        messages.append(summary_msg)
        messages.extend(recent_messages)

    def get_stats(self) -> dict:
        return {
            "compress_count": self._compress_count,
            "total_tokens_saved": self._total_tokens_saved,
            "trigger_tokens": self._trigger_tokens,
            "keep_recent": self._keep_recent,
        }
