---
name: deepagents
description: "Deep Agents (langchain-ai/deepagents) — 基于 LangGraph 的开箱即用 Agent 框架。适用于构建具备子代理、文件系统访问、上下文管理、技能加载、持久记忆、人机协作等能力的 AI Agent。涵盖 SDK 用法、CLI、中间件架构、后端、Profile 系统和部署模式。"
license: MIT
---

# Deep Agents 技能

> **包名**: `deepagents` (PyPI) · **仓库**: [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) · **版本**: 0.6.x · **要求**: Python ≥3.11

Deep Agents 是一个基于 LangGraph 构建的、开箱即用的 Agent 框架。它在底层提供了规划、文件系统访问、子代理委派、上下文管理、技能加载、持久记忆和人机协作等能力——每一层都可以组合和覆盖。

## 适用场景

- 构建需要工具调用、文件读写、Shell 访问或多步骤规划的 AI Agent
- 将任务委派给具有独立上下文窗口的子代理
- 按需加载可复用的技能（工作流）
- 通过自动摘要管理长对话上下文
- 跨会话持久化记忆（AGENTS.md 模式）
- 使用 LangSmith 将 Agent 部署到生产环境
- 构建编程助手、研究 Agent、内容写作 Agent 等

## 不适用场景

- 简单的单轮对话机器人 → 直接使用 `langchain`
- 自定义图拓扑 → 直接使用 `langgraph`
- 零依赖要求 → `deepagents` 会拉取 `langchain`、`langchain-anthropic`、`langchain-google-genai`、`langgraph`、`langsmith`

---

## 快速开始

```bash
uv add deepagents
# 或: pip install deepagents
```

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[my_custom_tool],
    system_prompt="你是一个研究助手。",
)
result = agent.invoke({"messages": "研究 LangGraph 并写一份摘要"})
```

---

## 架构概览

```
create_deep_agent()
├── 模型解析 (init_chat_model + ProviderProfile)
├── 中间件栈 (有序、可组合)
│   ├── TodoListMiddleware          — 任务规划清单
│   ├── SkillsMiddleware            — 按需加载技能
│   ├── FilesystemMiddleware        — read/write/edit/glob/grep/ls/execute
│   ├── SubAgentMiddleware          — task() 工具用于委派
│   ├── SummarizationMiddleware     — 自动上下文压缩
│   ├── PatchToolCallsMiddleware    — 工具调用修复
│   ├── AnthropicPromptCaching     — 缓存优化 (非 Anthropic 模型为空操作)
│   ├── MemoryMiddleware            — AGENTS.md 注入
│   ├── HumanInTheLoopMiddleware    — 审批/拒绝工具调用
│   └── [用户中间件]                — 自定义中间件
├── 后端 (可插拔存储)
│   ├── FilesystemBackend           — 直接文件系统
│   ├── StateBackend                — 内存临时存储
│   ├── StoreBackend                — LangGraph Store 持久化
│   ├── CompositeBackend            — 分层后端
│   ├── LocalShellBackend           — 文件系统 + Shell 执行
│   └── ContextHubBackend           — 上下文聚合
└── Harness Profile (模型特定调优)
    ├── 系统提示词后缀/覆盖
    ├── 工具描述覆盖
    ├── 额外中间件
    └── 排除的工具/中间件
```

### 核心概念

| 概念 | 说明 |
|------|------|
| **中间件 (Middleware)** | 拦截每次 LLM 调用——注入提示词、过滤工具、转换消息、跟踪状态 |
| **后端 (Backend)** | 可插拔的文件/技能/记忆存储——文件系统、内存、远程 |
| **Harness Profile** | 模型特定的运行时调优（提示词、工具可见性、中间件） |
| **Provider Profile** | 模型构建时的配置（API 参数、请求头） |
| **子代理 (Sub-Agent)** | 具有独立上下文窗口的隔离 Agent，通过 `task()` 工具委派 |
| **技能 (Skill)** | 从 SKILL.md 文件按需加载的可复用工作流 |
| **记忆 (Memory)** | 注入系统提示词的 AGENTS.md 文件，提供持久上下文 |

---

## 核心 API: `create_deep_agent`

```python
def create_deep_agent(
    model: str | BaseChatModel,              # "openai:gpt-5.5" 或模型实例
    *,
    tools: list[BaseTool | Callable] = None,  # 自定义工具
    system_prompt: str | SystemMessage = None, # 追加到基础提示词
    subagents: list[SubAgent] = None,         # 子代理定义
    async_subagents: list[AsyncSubAgent] = None, # 远程/异步子代理
    middleware: list[AgentMiddleware] = None,  # 自定义中间件
    skills: list[str] = None,                 # 技能源路径
    memory: list[str] = None,                 # AGENTS.md 路径
    permissions: list[FilesystemPermission] = None,  # 文件系统访问规则
    interrupt_on: dict = None,                # 人机协作配置
    backend: BackendProtocol = None,          # 存储后端
    response_format: ResponseFormat = None,   # 结构化输出
    state_schema: type = DeepAgentState,      # 自定义状态 schema
    context_schema: type = None,              # 上下文 schema
    checkpointer: Checkpointer = None,        # 持久化
    store: BaseStore = None,                  # 跨会话存储
    debug: bool = False,
    name: str = "deep_agent",
    cache: BaseCache = None,
) -> CompiledStateGraph
```

**返回值**: 编译后的 LangGraph `StateGraph` — 使用 `.invoke()`、`.ainvoke()`、`.stream()`、`.astream()` 调用。

---

## 中间件参考

### FilesystemMiddleware

提供工具: `ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`、`execute`（后端支持时）。

```python
from deepagents import FilesystemMiddleware, FilesystemPermission

# 权限: 对读/写操作执行 allow/deny/interrupt
permissions = [
    FilesystemPermission(operations=["read"], paths=["/src/**"], mode="allow"),
    FilesystemPermission(operations=["write"], paths=["/secrets/**"], mode="deny"),
    FilesystemPermission(operations=["write"], paths=["/prod/**"], mode="interrupt"),
]
```

### SubAgentMiddleware

通过 `task()` 工具将任务委派给子代理。

```python
subagents = [
    {
        "name": "researcher",
        "description": "进行网络研究并保存结果",
        "system_prompt": "你是一个研究专家...",
        "tools": [web_search_tool],
        "model": "openai:gpt-5.5",           # 可选: 模型覆盖
        "permissions": [FilesystemPermission(...)],  # 可选: 文件系统规则
        "skills": ["/skills/research/"],      # 可选: 技能
    },
    {
        "name": "reviewer",
        "description": "审查代码质量和安全性",
        "system_prompt": "你是一个代码审查员...",
        "response_format": ReviewFindings,    # 结构化输出 (Pydantic 模型)
    },
]
```

子代理默认继承主代理的中间件栈（文件系统、摘要等），除非显式覆盖。

### SummarizationMiddleware

当 token 使用量超过阈值时自动压缩对话。

```python
from deepagents.middleware.summarization import SummarizationMiddleware

# 在上下文使用 85% 时自动触发，保留 10% 的近期消息
summ = SummarizationMiddleware(
    model="openai:gpt-5.4-mini",
    backend=backend,
    trigger=("fraction", 0.85),
    keep=("fraction", 0.10),
)
```

被卸载的消息存储在 `/conversation_history/{thread_id}.md`。

### MemoryMiddleware

将 AGENTS.md 文件加载到系统提示词中，提供持久上下文。

```python
agent = create_deep_agent(
    memory=[
        "~/.deepagents/AGENTS.md",      # 用户级
        "./.deepagents/AGENTS.md",       # 项目级
    ],
)
```

HTML 注释会被剥离。内容按顺序拼接。

### SkillsMiddleware

从 SKILL.md 文件加载可复用技能（带 YAML 前置元数据）。

```python
agent = create_deep_agent(
    skills=[
        "/skills/base/",
        "/skills/user/",
        "/skills/project/",
    ],
)
```

技能目录结构：
```
/skills/my-skill/
├── SKILL.md          # 必需: YAML 前置元数据 + Markdown 说明
└── helper.py         # 可选: 辅助文件
```

SKILL.md 格式：
```markdown
---
name: my-skill
description: 这个技能做什么 (最多 1024 字符)
---

# 我的技能

## 何时使用
- 条件 1
- 条件 2

## 步骤
1. 做这个
2. 做那个
```

### RubricMiddleware

自评估迭代：定义质量标准，由评审子代理评估输出，Agent 循环执行直到满足标准。

```python
from deepagents.middleware.rubric import RubricMiddleware, RubricEvaluation

rubric = RubricMiddleware(
    evaluation=RubricEvaluation(
        criteria=[
            {"name": "completeness", "description": "所有章节已覆盖"},
            {"name": "accuracy", "description": "无事实错误"},
        ],
    ),
    grader_model="openai:gpt-5.4-mini",
    max_iterations=3,
)
```

### HumanInTheLoopMiddleware

在敏感工具调用前暂停执行，等待人工审批。

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    interrupt_on={
        "write_file": True,
        "execute": {"allowlist": ["ls", "cat"]},
    },
    checkpointer=checkpointer,  # HITL 需要 checkpointer
)
```

---

## 后端参考

| 后端 | 使用场景 |
|------|---------|
| `FilesystemBackend(root_dir)` | 直接文件系统访问（本地开发、CI） |
| `StateBackend()` | 内存临时存储（测试、无状态） |
| `StoreBackend(store)` | LangGraph Store 持久化（生产） |
| `CompositeBackend(layers)` | 分层: 如从 FS 读取，写入到 state |
| `LocalShellBackend(root_dir)` | 文件系统 + 无限制 Shell（仅限本地开发） |
| `ContextHubBackend()` | 跨源上下文聚合 |

```python
from deepagents.backends import FilesystemBackend, CompositeBackend, StateBackend

# 直接文件系统
backend = FilesystemBackend(root_dir="/workspace")

# 组合: 从文件系统读取，写入到内存
backend = CompositeBackend(
    read_backend=FilesystemBackend(root_dir="/workspace"),
    write_backend=StateBackend(),
)
```

---

## Profile 系统

### Harness Profile（运行时调优）

控制每个模型/提供商的提示词组装、工具可见性和中间件。

```python
from deepagents import HarnessProfile, HarnessProfileConfig, register_harness_profile

profile = HarnessProfile(
    key="my-custom",
    config=HarnessProfileConfig(
        base_system_prompt="自定义系统提示词...",
        system_prompt_suffix="额外指令...",
        tool_description_overrides={"task": "自定义任务描述..."},
        excluded_tools=["execute"],
    ),
)
register_harness_profile(profile)
```

内置 Profile 支持: Anthropic Sonnet/Opus/Haiku、OpenAI Codex。

### Provider Profile（模型构建）

控制模型初始化时的 API 参数。

```python
from deepagents import ProviderProfile, register_provider_profile

register_provider_profile(ProviderProfile(
    key="my-provider",
    match_spec="my-provider:",
    init_kwargs={"base_url": "https://custom.api.com/v1"},
))
```

---


## SDK 调用方式

Deep Agents 返回 `CompiledStateGraph`，支持 4 种调用模式：

```python
from deepagents import create_deep_agent

agent = create_deep_agent(model="openai:gpt-5.5", tools=[...])

# 同步调用
result = agent.invoke({"messages": "你的任务"})
print(result["messages"][-1].content)

# 异步调用
result = await agent.ainvoke({"messages": "你的任务"})

# 同步流式
for chunk in agent.stream({"messages": "你的任务"}, stream_mode="values"):
    last = chunk["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        for tc in last.tool_calls:
            print(f">> {tc['name']}({tc['args']})")
    if last.type == "ai" and last.content:
        print(last.content)

# 异步流式 (适合 SSE/WebSocket 推送)
async for chunk in agent.astream({"messages": "你的任务"}, stream_mode="values"):
    ...

# 多轮对话 (带 checkpointer 记忆上下文)
from langgraph.checkpoint.memory import MemorySaver
agent = create_deep_agent(model="openai:gpt-5.5", tools=[...], checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "session-001"}}
await agent.ainvoke({"messages": "第一轮"}, config=config)
await agent.ainvoke({"messages": "第二轮，记得上文"}, config=config)

# 仅使用工具 (跳过 LLM)
from deepagents import create_deep_agent
my_tool.invoke({"param": "value"})
```
## 使用模式与示例

### 模式 1: 研究 Agent

```python
from deepagents import create_deep_agent

research_sub = {
    "name": "researcher",
    "description": "对单个主题进行深度研究",
    "system_prompt": "彻底研究。将结果保存到文件。",
    "tools": [tavily_search, think_tool],
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    tools=[tavily_search, think_tool],
    subagents=[research_sub],
    system_prompt="你是一个研究协调器。将研究任务委派给子代理。",
)
```

### 模式 2: 带技能的内容写作 Agent

```python
agent = create_deep_agent(
    memory=["./AGENTS.md"],           # 品牌风格指南
    skills=["./skills/"],             # blog-post、social-media 技能
    tools=[generate_cover],
    backend=FilesystemBackend(root_dir="./output"),
)
```

### 模式 3: 带权限的编程 Agent

```python
from deepagents import FilesystemPermission

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    backend=LocalShellBackend(root_dir="/workspace"),
    permissions=[
        FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/src/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/secrets/**"], mode="deny"),
    ],
    interrupt_on={"execute": True},
    checkpointer=checkpointer,
)
```

### 模式 4: 结构化输出子代理

```python
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    summary: str
    confidence: float
    findings: list[str]

analyst_sub = {
    "name": "analyst",
    "description": "分析数据并返回结构化结果",
    "system_prompt": "彻底分析数据。",
    "response_format": AnalysisResult,
}
```

### 模式 5: 流式输出

```python
async for chunk in agent.astream(
    {"messages": [("user", task)]},
    config={"configurable": {"thread_id": "my-thread"}},
    stream_mode="values",
):
    if "messages" in chunk:
        for msg in chunk["messages"]:
            # 处理消息
            pass
```

---

## 模型字符串格式

使用 `provider:model-name` 约定：
- `"openai:gpt-5.5"` — OpenAI
- `"anthropic:claude-sonnet-4-5-20250929"` — Anthropic
- `"google_genai:gemini-2.5-pro"` — Google
- `"ollama:llama3"` — 本地 Ollama
- `"fireworks:accounts/fireworks/models/llama-v3p1-70b"` — Fireworks AI

也可以直接传入预配置的 `BaseChatModel` 实例。

---

## 部署

### LangGraph Platform

创建 `langgraph.json`：
```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./agent.py:agent"
  }
}
```

通过 `deepagents deploy` CLI 或 LangSmith 部署。

### LangSmith 集成

- 设置 `LANGCHAIN_TRACING_V2=true` 启用自动追踪
- 评估套件位于 `libs/evals/`
- 通过 LangSmith 部署服务部署

---

## CLI (deepagents-code)

```bash
# 安装
curl -LsSf https://langch.in/dcode | bash

# 运行
deepagents-code

# 命令
deepagents-code chat          # 交互式对话
deepagents-code deploy        # 部署到 LangSmith
deepagents-code config        # 管理配置
```

---

## 依赖

```
langchain-core >=1.4.0,<2.0.0
langchain >=1.3.4,<2.0.0
langchain-anthropic >=1.4.3,<2.0.0
langchain-google-genai >=4.2.2,<5.0.0
langsmith >=0.8.3
wcmatch
```

可选: `langchain-quickjs` 用于 JS 沙箱执行。

---

## 参考文档

- [完整架构](references/architecture.md) — 中间件/后端内部机制详解
- [API 参考](references/api-reference.md) — 所有公开类和类型
- [示例合集](references/examples.md) — 来自仓库的工作模式
- [官方文档](https://docs.langchain.com/oss/python/deepagents/overview)
- [API 文档](https://reference.langchain.com/python/deepagents/)


