# Deep Agents 架构详解

## 中间件管线

中间件是有序且可组合的。每个中间件可以：
- **wrap_model_call()** — 在每次 LLM 请求发送前拦截
- **动态过滤工具** — 按调用过滤可用工具
- **注入系统提示词** — 向系统消息添加上下文
- **转换消息** — 摘要、截断、驱逐
- **维护跨轮次状态** — 通过类型化状态字典

### 执行顺序 (create_deep_agent)

```
 1. TodoListMiddleware           — 任务规划清单
 2. _ToolExclusionMiddleware     — 移除 Profile 排除的工具
 3. SkillsMiddleware             — 将 SKILL.md 加载到系统提示词
 4. FilesystemMiddleware         — 提供文件系统工具 (ls, read, write, edit, glob, grep, execute)
 5. SubAgentMiddleware           — 提供 task() 工具用于委派
 6. SummarizationMiddleware      — token 超阈值时自动压缩
 7. PatchToolCallsMiddleware     — 修复格式错误的工具调用
 8. [用户中间件]                 — 通过 middleware=[] 传入的自定义中间件
 9. [Profile 额外中间件]         — Harness Profile 特定的附加中间件
10. _ToolExclusionMiddleware     — Profile 排除工具的强制执行
11. AnthropicPromptCaching       — 非 Anthropic 模型为空操作，Anthropic 模型设置缓存断点
12. MemoryMiddleware             — 将 AGENTS.md 加载到系统提示词
13. HumanInTheLoopMiddleware     — 暂停等待人工审批
```

### 中间件状态 Schema

每个中间件可以声明一个带类型字段的 `state_schema`。以 `_` 为前缀的私有字段在中间件间隔离。公共字段在 Agent 状态中共享。

```python
class SummarizationState(AgentState):
    _summarization_events: Annotated[list, PrivateStateAttr(default_factory=list)]
```

---

## 后端协议

所有后端实现 `BackendProtocol`：

```python
class BackendProtocol(ABC):
    async def ls(self, path: str) -> LsResult
    async def read_file(self, path: str, ...) -> ReadResult
    async def write_file(self, path: str, content: str, ...) -> WriteResult
    async def edit_file(self, path: str, ...) -> EditResult
    async def glob(self, pattern: str, ...) -> GlobResult
    async def grep(self, pattern: str, ...) -> GrepResult
```

沙箱后端额外实现 `SandboxBackendProtocol`：
```python
class SandboxBackendProtocol(BackendProtocol):
    async def execute(self, command: str, ...) -> ExecuteResponse
```

### FilesystemBackend 内部机制

- 使用 `wcmatch.glob` 处理 glob/grep 模式（支持 `**`、`{a,b}` 等）
- 优先使用 `rg`（ripgrep）进行 grep，不可用时回退到 Python
- `virtual_mode=True` 启用基于路径的防护（禁止 `..`、`~`、root_dir 外的绝对路径）
- 文件格式 v2: `content` 为纯 `str`（UTF-8 或 base64），带 `encoding` 字段

### CompositeBackend

为读写分离而后置分层：
```python
backend = CompositeBackend(
    read_backend=FilesystemBackend(root_dir="/workspace"),
    write_backend=StateBackend(),  # 写入保留在内存中
)
```

### StoreBackend

持久化到 LangGraph 的 `BaseStore`，实现跨会话记忆：
```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
backend = StoreBackend(store=store)
```

---

## 子代理系统

### 同步子代理 (SubAgentMiddleware)

- 每个子代理是一个完整的 `create_agent()` 实例，拥有自己的中间件栈
- 默认继承主代理的工具（除非显式指定 `tools`）
- 默认继承主代理的权限（除非显式指定 `permissions`）
- 将最后一条消息内容作为 ToolMessage 返回（设置了 `response_format` 时返回结构化响应）
- 在 LangSmith 中作为子运行进行追踪

### 异步子代理 (AsyncSubAgentMiddleware)

- 通过 LangSmith 部署非阻塞运行
- 通过 `AsyncSubAgent` TypedDict 配置 `deployment_url`
- 即发即忘或轮询结果

### 通用子代理 (General-Purpose Sub-Agent)

当不存在名为 `general-purpose` 的子代理时自动添加：
- 继承主代理的模型和工具
- 通过 `task(subagent_type="general-purpose", ...)` 用于通用委派
- 可通过 `GeneralPurposeSubagentProfile` 禁用或自定义

---

## 上下文管理

### 摘要机制

- **触发条件**: token 使用量超过阈值（默认: 上下文窗口的 85%）
- **保留**: 保留近期消息（默认: 上下文窗口的 10%）
- **存储**: 被卸载的消息保存到 `/conversation_history/{thread_id}.md`
- **模型**: 使用更小/更便宜的模型进行摘要（如 gpt-5.4-mini）
- **工具消息驱逐**: 大型工具输出被卸载到磁盘，替换为预览

### 消息驱逐

大型工具输出（超过阈值）会被：
1. 卸载到 `/evicted_messages/{thread_id}/{message_id}.md`
2. 替换为包含前 N 行 + 截断提示的预览
3. Agent 可通过请求文件读取完整内容

### Delta Channel

`DeepAgentState` 在消息上使用 `DeltaChannel`，将检查点增长从 O(N²) 降低到 O(N)。每 50 条消息创建快照。

---

## 技能系统

### 技能发现

技能从配置的源（后端中的路径）加载。每个源被扫描以查找包含 `SKILL.md` 的目录。

### 技能元数据 (YAML 前置)

```yaml
---
name: my-skill           # 最多 64 字符，小写字母数字 + 连字符
description: 做什么      # 最多 1024 字符
license: MIT             # 可选
compatibility: [...]     # 可选
allowed_tools: [...]     # 可选的工具限制
---
```

### 渐进式披露

技能仅以元数据形式注入系统提示词。当 Agent 引用某个技能名称时，才加载完整说明。

### 源分层

后加载的源覆盖先加载的（同名时后者优先）：
```python
skills=[
    "/skills/base/",      # 基础技能
    "/skills/user/",      # 用户覆盖
    "/skills/project/",   # 项目特定
]
```

---

## 记忆系统 (AGENTS.md)

### AGENTS.md 规范

- 标准 Markdown，无必需结构
- HTML 注释（`<!-- ... -->`）在注入前被剥离
- 多个源按顺序拼接
- 始终加载（与按需加载的技能不同）

### 注入方式

记忆内容追加到基础 Agent 提示词之后的系统提示词中。与 Harness Profile 的提示词后缀组合。

---

## Harness Profile

### 解析顺序

1. 将模型规格与已注册的 Profile 匹配（先精确匹配，再前缀匹配）
2. 应用 Profile 配置: 基础提示词、后缀、工具覆盖、排除的工具/中间件
3. 与用户提供的配置合并（用户优先）

### Profile 配置字段

```python
@dataclass
class HarnessProfileConfig:
    base_system_prompt: str | None           # 完全替换基础提示词
    system_prompt_suffix: str | None         # 追加到基础提示词
    tool_description_overrides: dict         # 覆盖工具描述
    excluded_tools: list[str]                # 对 LLM 隐藏工具
    excluded_middleware: list                 # 从栈中移除中间件
    extra_middleware: list[AgentMiddleware]   # 添加中间件
    general_purpose_subagent: GeneralPurposeSubagentProfile  # 通用子代理配置
```

---

## Provider Profile

### 内置提供商

- **OpenAI**: 启用 Responses API，设置 `use_responses_api=True`
- **OpenRouter**: 添加应用归属头（`X-Title`、`HTTP-Referer`）

### 注册

```python
from deepagents import ProviderProfile, register_provider_profile

register_provider_profile(ProviderProfile(
    key="my-provider",
    match_spec="my-provider:",  # 前缀匹配 "provider:model" 字符串
    init_kwargs={"base_url": "...", "api_key": "..."},
))
```

---

## 安全模型

Deep Agents 遵循 **"信任 LLM"** 模型：
- Agent 可以执行其工具允许的任何操作
- 在工具/沙箱层面强制边界
- 使用 `FilesystemPermission` 进行基于路径的访问控制
- 使用 `HumanInTheLoopMiddleware` 处理敏感操作
- 对不受信任的工作负载使用沙箱后端（Docker、VM）
- `FilesystemBackend` + `LocalShellBackend` 授予完全的主机访问权限——仅在受信环境中使用

---

## 追踪与评估

- **LangSmith**: 设置 `LANGCHAIN_TRACING_V2=true` 启用自动追踪
- **运行元数据**: `ls_integration: "deepagents"`、版本信息、Agent 名称
- **评估**: `libs/evals/` 包含 Harbor 集成的评估套件
- **递归限制**: 默认 9,999
