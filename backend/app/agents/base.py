"""Agent 基类"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import StateBackend
from langchain.agents.middleware.types import AgentMiddleware


class BaseAgent(ABC):
    """智能体基类。"""

    SYSTEM_PROMPT: str = ""
    MODEL_SPEC: str = "openai:mimo-v2.5-pro"
    MODEL_BASE_URL: str = "https://sub2api-plus.zeabur.app/v1"
    MODEL_API_KEY: str = "sk-12344488b2ff7e6d0e8239885568007b688ca9478d161c02ad9f82062e0369a8"

    # 自动压缩开关
    ENABLE_SUMMARIZATION: bool = True
    SUMMARIZATION_TRIGGER_TOKENS: int = 8000
    SUMMARIZATION_KEEP_RECENT: int = 6

    def __init__(
        self,
        *,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        checkpointer=None,
        debug: bool = False,
    ):
        self.model = model or self.MODEL_SPEC
        self.base_url = base_url or self.MODEL_BASE_URL
        self.api_key = api_key or self.MODEL_API_KEY
        self.checkpointer = checkpointer
        self.debug = debug
        self._compiled = None

    @abstractmethod
    def _build_tools(self) -> list:
        ...

    def _build_subagents(self) -> list[dict]:
        return []

    def _build_middleware(self) -> list[AgentMiddleware]:
        return []

    def _get_skills_path(self) -> list[str]:
        import importlib
        try:
            mod = importlib.import_module(self.__class__.__module__)
            agent_dir = Path(mod.__file__).parent
            skills_dir = agent_dir / "skills"
            if skills_dir.is_dir():
                return [str(skills_dir)]
        except Exception:
            pass
        return []

    def _get_summarization_middleware(self) -> list[AgentMiddleware]:
        """构建自动压缩中间件。"""
        if not self.ENABLE_SUMMARIZATION:
            return []
        from app.agents.middleware.summarization import SummarizationMiddleware
        return [SummarizationMiddleware(
            trigger_tokens=self.SUMMARIZATION_TRIGGER_TOKENS,
            keep_recent=self.SUMMARIZATION_KEEP_RECENT,
        )]

    def create(self):
        if self._compiled is not None:
            return self._compiled

        chat_model = init_chat_model(self.model, base_url=self.base_url, api_key=self.api_key)

        # 中间件栈: 专用 + 自动压缩
        middleware = self._build_middleware() + self._get_summarization_middleware()

        self._compiled = create_deep_agent(
            model=chat_model,
            tools=self._build_tools(),
            subagents=self._build_subagents(),
            middleware=middleware if middleware else None,
            skills=self._get_skills_path() or None,
            backend=StateBackend(),
            permissions=[
                FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
                FilesystemPermission(operations=["write"], paths=["/output/**"], mode="allow"),
            ],
            checkpointer=self.checkpointer,
            debug=self.debug,
            system_prompt=self.SYSTEM_PROMPT,
        )
        return self._compiled

    def invoke(self, messages: str, config: dict | None = None):
        return self.create().invoke({"messages": messages}, config=config)

    async def ainvoke(self, messages: str, config: dict | None = None):
        return await self.create().ainvoke({"messages": messages}, config=config)

    def stream(self, messages: str, stream_mode: str = "values", config: dict | None = None):
        return self.create().stream({"messages": messages}, stream_mode=stream_mode, config=config)

    async def astream(self, messages: str, stream_mode: str = "values", config: dict | None = None):
        return self.create().astream({"messages": messages}, stream_mode=stream_mode, config=config)
