# Deep Agents API 参考

## 顶层导出

```python
from deepagents import (
    # 主入口
    create_deep_agent,
    DeepAgentState,

    # 中间件
    FilesystemMiddleware,
    FilesystemPermission,
    SubAgentMiddleware,
    SubAgent,
    CompiledSubAgent,
    AsyncSubAgentMiddleware,
    AsyncSubAgent,
    MemoryMiddleware,
    RubricMiddleware,

    # Profile
    HarnessProfile,
    HarnessProfileConfig,
    GeneralPurposeSubagentProfile,
    register_harness_profile,
    ProviderProfile,
    register_provider_profile,
)
```

---

## `create_deep_agent`

```python
def create_deep_agent(
    model: str | BaseChatModel,
    *,
    tools: list[BaseTool | Callable | dict[str, Any]] | None = None,
    system_prompt: str | SystemMessage | None = None,
    subagents: Sequence[SubAgent | CompiledStateGraph] | None = None,
    async_subagents: Sequence[AsyncSubAgent] | None = None,
    middleware: Sequence[AgentMiddleware] | None = None,
    skills: Sequence[str | tuple[str, str]] | None = None,
    memory: Sequence[str] | None = None,
    permissions: Sequence[FilesystemPermission] | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    backend: BackendProtocol | None = None,
    response_format: ResponseFormat | type | dict | None = None,
    state_schema: type[AgentState] | None = DeepAgentState,
    context_schema: type[BaseModel] | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    debug: bool = False,
    name: str = "deep_agent",
    cache: BaseCache | None = None,
) -> CompiledStateGraph
```

创建一个完全配置的 Deep Agent，所有中间件已组合完毕。

**参数说明：**
- `model` — 模型字符串（`"provider:model"`）或 `BaseChatModel` 实例
- `tools` — 自定义工具（函数、`BaseTool` 或字典工具）
- `system_prompt` — 追加到基础提示词的额外指令
- `subagents` — 子代理定义或编译后的 LangGraph 图
- `async_subagents` — 远程/异步子代理配置
- `middleware` — 额外中间件（插入到内置层之间）
- `skills` — 后端中技能源的路径
- `memory` — 后端中 AGENTS.md 文件的路径
- `permissions` — 文件系统访问规则
- `interrupt_on` — 人机协作工具审批配置
- `backend` — 存储后端（默认: `StateBackend()`）
- `response_format` — 结构化输出 schema
- `state_schema` — 自定义 Agent 状态 schema（默认: `DeepAgentState`）
- `context_schema` — 运行时上下文 schema
- `checkpointer` — LangGraph checkpointer，用于持久化/人机协作
- `store` — LangGraph store，用于跨会话持久化
- `debug` — 启用调试日志
- `name` — Agent 名称（用于追踪）
- `cache` — LangGraph 缓存后端

**返回值:** `CompiledStateGraph` — 使用 `.invoke()`、`.ainvoke()`、`.stream()`、`.astream()` 调用

---

## 状态

### `DeepAgentState`

```python
class DeepAgentState(AgentState):
    messages: Required[Annotated[list[AnyMessage], DeltaChannel(...)]]
```

默认状态 schema，使用 Delta 压缩消息以实现高效检查点。

---

## 中间件类

### `FilesystemMiddleware`

```python
class FilesystemMiddleware(AgentMiddleware):
    def __init__(
        self,
        backend: BackendProtocol,
        custom_tool_descriptions: dict[str, str] | None = None,
        _permissions: list[FilesystemPermission] | None = None,
    )
```

提供文件系统工具: `ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`、`execute`。

### `FilesystemPermission`

```python
@dataclass
class FilesystemPermission:
    operations: list[Literal["read", "write"]]
    paths: list[str]              # Glob 模式，必须以 "/" 开头
    mode: Literal["allow", "deny", "interrupt"] = "allow"
```

- `allow` — 操作继续执行
- `deny` — 返回权限拒绝错误
- `interrupt` — 暂停等待人工审批

### `SubAgentMiddleware`

```python
class SubAgentMiddleware(AgentMiddleware):
    def __init__(
        self,
        backend: BackendProtocol,
        subagents: Sequence[SubAgent | CompiledStateGraph],
        task_description: str | None = None,
        state_schema: type | None = None,
    )
```

提供 `task()` 工具用于向子代理委派任务。

### `SubAgent` (TypedDict)

```python
class SubAgent(TypedDict):
    name: str                              # 必需: 唯一标识符
    description: str                       # 必需: 功能描述
    system_prompt: str                     # 必需: 指令
    tools: NotRequired[Sequence[BaseTool]] # 可选: 默认继承主代理
    model: NotRequired[str | BaseChatModel]  # 可选: "provider:model"
    middleware: NotRequired[list[AgentMiddleware]]
    interrupt_on: NotRequired[dict[str, bool | InterruptOnConfig]]
    skills: NotRequired[list[str]]
    permissions: NotRequired[list[FilesystemPermission]]
    response_format: NotRequired[ResponseFormat | type | dict]
```

### `AsyncSubAgent` (TypedDict)

```python
class AsyncSubAgent(TypedDict):
    name: str
    description: str
    deployment_url: str                    # LangSmith 部署 URL
    api_key: NotRequired[str]
```

### `MemoryMiddleware`

```python
class MemoryMiddleware(AgentMiddleware):
    def __init__(
        self,
        backend: BackendProtocol,
        sources: Sequence[str],
        add_cache_control: bool = True,
    )
```

将 AGENTS.md 文件加载到系统提示词中。

### `SkillsMiddleware`

```python
class SkillsMiddleware(AgentMiddleware):
    def __init__(
        self,
        backend: BackendProtocol,
        sources: Sequence[str | tuple[str, str]],
    )
```

通过渐进式披露加载 SKILL.md 文件。

### `RubricMiddleware`

```python
class RubricMiddleware(AgentMiddleware):
    def __init__(
        self,
        evaluation: RubricEvaluation,
        grader_model: str | BaseChatModel,
        max_iterations: int = 3,
        grader_tools: list[BaseTool] | None = None,
    )
```

带评审子代理的自评估迭代。

### `SummarizationMiddleware`

```python
class SummarizationMiddleware(AgentMiddleware):
    def __init__(
        model: str | BaseChatModel,
        backend: BackendProtocol,
        trigger: tuple[str, float] = ("fraction", 0.85),
        keep: tuple[str, float] = ("fraction", 0.10),
    )
```

当 token 使用量超过阈值时自动压缩对话。

---

## 后端类

### `BackendProtocol` (ABC)

```python
class BackendProtocol(ABC):
    async def ls(self, path: str) -> LsResult
    async def read_file(self, path: str, offset: int = 0, limit: int | None = None) -> ReadResult
    async def write_file(self, path: str, content: str, create_dirs: bool = True) -> WriteResult
    async def edit_file(self, path: str, old_string: str, new_string: str, ...) -> EditResult
    async def glob(self, pattern: str, path: str = "/") -> GlobResult
    async def grep(self, pattern: str, path: str = "/", ...) -> GrepResult
```

### `SandboxBackendProtocol` (扩展 BackendProtocol)

```python
class SandboxBackendProtocol(BackendProtocol):
    async def execute(self, command: str, timeout: int = 120) -> ExecuteResponse
```

### 后端实现

| 类 | 说明 |
|---|------|
| `FilesystemBackend(root_dir, virtual_mode, max_file_size_mb)` | 直接文件系统 |
| `StateBackend()` | 内存临时存储 |
| `StoreBackend(store, namespace_factory)` | LangGraph Store |
| `CompositeBackend(read_backend, write_backend)` | 分层后端 |
| `LocalShellBackend(root_dir)` | 文件系统 + Shell |
| `ContextHubBackend()` | 上下文聚合 |

---

## Profile 类

### `HarnessProfile`

```python
@dataclass
class HarnessProfile:
    key: str                              # 唯一标识符
    config: HarnessProfileConfig          # 运行时配置
    priority: int = 0                     # 越高 = 解析越靠后
    match_fn: Callable[[BaseChatModel], bool] | None = None
```

### `HarnessProfileConfig`

```python
@dataclass
class HarnessProfileConfig:
    base_system_prompt: str | None = None
    system_prompt_suffix: str | None = None
    tool_description_overrides: dict[str, str] = field(default_factory=dict)
    excluded_tools: list[str] = field(default_factory=list)
    excluded_middleware: list[type | str] = field(default_factory=list)
    extra_middleware: list[AgentMiddleware] = field(default_factory=list)
    general_purpose_subagent: GeneralPurposeSubagentProfile = field(...)
```

### `GeneralPurposeSubagentProfile`

```python
@dataclass(frozen=True)
class GeneralPurposeSubagentProfile:
    enabled: bool | None = None       # None=继承, True=强制启用, False=禁用
    description: str | None = None
    system_prompt: str | None = None
```

### `ProviderProfile`

```python
@dataclass
class ProviderProfile:
    key: str
    match_spec: str                   # 前缀匹配 "provider:model"
    init_kwargs: dict[str, Any] = field(default_factory=dict)
```

---

## 结果类型

### `ReadResult`
```python
class ReadResult(TypedDict):
    content: str
    total_lines: int
    is_truncated: bool
```

### `WriteResult`
```python
class WriteResult(TypedDict):
    path: str
    bytes_written: int
```

### `EditResult`
```python
class EditResult(TypedDict):
    path: str
    old_string: str
    new_string: str
    occurrences: int
```

### `GrepResult`
```python
class GrepResult(TypedDict):
    matches: list[GrepMatch]
    truncated: bool
```

### `GrepMatch`
```python
class GrepMatch(TypedDict):
    path: str
    line_number: int
    line: str
```

### `LsResult`
```python
class LsResult(TypedDict):
    entries: list[FileInfo]
```

### `GlobResult`
```python
class GlobResult(TypedDict):
    files: list[str]
```

### `ExecuteResponse`
```python
class ExecuteResponse(TypedDict):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
```
