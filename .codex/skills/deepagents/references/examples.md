# Deep Agents 示例合集

## 示例 1: 研究 Agent (深度研究)

多 Agent 研究模式，带子代理委派和网络搜索。

```python
from datetime import datetime
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langchain_core.tools import tool

@tool
def tavily_search(query: str, max_results: int = 5) -> dict:
    """使用 Tavily API 搜索网络。"""
    from tavily import TavilyClient
    client = TavilyClient()
    return client.search(query, max_results=max_results)

@tool
def think_tool(thought: str) -> str:
    """记录思考步骤，用于策略性反思。"""
    return f"已记录: {thought}"

# 子代理: 专注研究
research_sub = {
    "name": "research-agent",
    "description": "对单个主题进行深度研究。每次只给一个主题。",
    "system_prompt": f"""你是一个研究专家。
当前日期: {datetime.now():%Y-%m-%d}

## 指令
1. 使用 tavily_search 搜索信息
2. 使用 think_tool 反思发现
3. 综合为一份全面的报告
4. 包含来源和置信度""",
    "tools": [tavily_search, think_tool],
}

# 主协调器
agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-5-20250929", temperature=0.0),
    tools=[tavily_search, think_tool],
    system_prompt="""你是一个研究协调器。
1. 将用户的问题拆分为研究子主题
2. 将每个子主题委派给 research-agent 子代理
3. 综合所有发现为最终全面的答案""",
    subagents=[research_sub],
)

# 运行
result = agent.invoke({"messages": "AI Agent 的最新进展有哪些？"})
```

---

## 示例 2: 带技能的内容写作 Agent

通过文件系统配置的 Agent: AGENTS.md 定义品牌风格，skills 提供工作流。

### 目录结构
```
content-builder/
├── AGENTS.md                    # 品牌风格指南
├── content_writer.py            # Agent 入口
├── subagents.yaml               # 子代理定义
├── skills/
│   ├── blog-post/
│   │   └── SKILL.md             # 博客写作工作流
│   └── social-media/
│       └── SKILL.md             # 社交媒体工作流
└── blogs/                       # 输出目录
```

### Agent 代码
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
import yaml

def load_subagents(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return [
        {
            "name": name,
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
            "tools": [web_search],
        }
        for name, spec in config.items()
    ]

agent = create_deep_agent(
    memory=["./AGENTS.md"],
    skills=["./skills/"],
    tools=[generate_cover, generate_social_image],
    subagents=load_subagents("subagents.yaml"),
    backend=FilesystemBackend(root_dir="."),
)
```

### 技能: blog-post/SKILL.md
```markdown
---
name: blog-post
description: 撰写长篇博客文章，含 SEO 优化和封面图生成。
---

# 博客写作技能

## 先研究（必需）
写作前，使用 task 工具委派研究:
```
task(subagent_type="researcher", description="研究 [主题]")
```

## 输出结构
```
blogs/<slug>/
├── post.md        # 博客内容
└── hero.png       # 封面图（必需）
```

## 文章结构
1. 开头钩子（2-3 句）
2. 背景（为什么重要）
3. 主要内容（3-5 个 H2 章节）
4. 实践应用
5. 总结与行动号召
```

---

## 示例 3: 带文件系统权限的编程 Agent

带读写权限和人机协作的本地编程助手。

```python
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import LocalShellBackend
from langgraph.checkpoint.memory import MemorySaver

permissions = [
    FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
    FilesystemPermission(operations=["write"], paths=["/src/**"], mode="allow"),
    FilesystemPermission(operations=["write"], paths=["/tests/**"], mode="allow"),
    FilesystemPermission(operations=["write"], paths=["/secrets/**"], mode="deny"),
    FilesystemPermission(operations=["write"], paths=["/prod/**"], mode="interrupt"),
]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    backend=LocalShellBackend(root_dir="/workspace"),
    permissions=permissions,
    interrupt_on={"execute": True},
    checkpointer=MemorySaver(),
    system_prompt="""你是一个编程助手。
- 编辑前先读取文件
- 修改后运行测试
- 遵循现有代码模式""",
)
```

---

## 示例 4: Text-to-SQL Agent (带技能)

将自然语言转换为 SQL 查询的 Agent。

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    model="openai:gpt-5.5",
    memory=["./AGENTS.md"],       # Schema 文档、约定
    skills=[
        "./skills/schema-exploration/",
        "./skills/query-writing/",
    ],
    backend=FilesystemBackend(root_dir="."),
    system_prompt="你是一个 SQL 专家。将自然语言转换为优化的查询。",
)
```

### 技能: schema-exploration/SKILL.md
```markdown
---
name: schema-exploration
description: 探索数据库 schema 并记录表关系。
---

# Schema 探索

## 步骤
1. 列出可用表
2. 读取相关表的 schema 定义
3. 记录关系（外键、连接）
4. 保存结果到 schema-notes.md
```

---

## 示例 5: 结构化输出子代理

返回类型化结构数据的子代理。

```python
from pydantic import BaseModel, Field
from deepagents import create_deep_agent

class CodeReview(BaseModel):
    issues: list[str] = Field(description="发现的问题列表")
    severity: str = Field(description="整体严重程度: low/medium/high/critical")
    suggestions: list[str] = Field(description="改进建议")
    approved: bool = Field(description="代码是否通过审查")

reviewer_sub = {
    "name": "code-reviewer",
    "description": "审查代码并返回结构化结果",
    "system_prompt": "审查代码中的 bug、安全问题和风格。",
    "tools": [],
    "response_format": CodeReview,
}

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[reviewer_sub],
)

# task() 工具将以 JSON 形式返回结构化的 CodeReview
```

---

## 示例 6: 流式输出 (Rich 展示)

```python
import asyncio
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from deepagents import create_deep_agent

console = Console()

async def run_agent(task: str):
    agent = create_deep_agent(model="openai:gpt-5.5")
    printed = 0

    with Live(Spinner("dots", "思考中..."), console=console, transient=True) as live:
        async for chunk in agent.astream(
            {"messages": [("user", task)]},
            config={"configurable": {"thread_id": "demo"}},
            stream_mode="values",
        ):
            if "messages" in chunk:
                msgs = chunk["messages"]
                if len(msgs) > printed:
                    live.stop()
                    for msg in msgs[printed:]:
                        if hasattr(msg, "content") and msg.content:
                            console.print(Panel(str(msg.content), title=type(msg).__name__))
                    printed = len(msgs)
                    live.start()

asyncio.run(run_agent("解释 Deep Agents 中中间件的工作原理"))
```

---

## 示例 7: Ralph 模式 (持久循环)

单所有者的完成/验证循环模式。

```python
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.middleware.rubric import RubricMiddleware, RubricEvaluation

# 自评估质量标准
rubric = RubricMiddleware(
    evaluation=RubricEvaluation(
        criteria=[
            {"name": "completeness", "description": "所有需求已实现"},
            {"name": "tests_pass", "description": "所有测试通过"},
            {"name": "no_regressions", "description": "没有破坏现有功能"},
        ],
    ),
    grader_model="openai:gpt-5.4-mini",
    max_iterations=3,
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[rubric],
    permissions=[
        FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/src/**"], mode="allow"),
    ],
    system_prompt="""你是一个持久实现 Agent。
1. 理解任务
2. 规划实现方案
3. 实现变更
4. 运行测试
5. 对照需求验证
6. 如果测试失败，调试并修复""",
)
```

---

## 示例 8: REPL Swarm (多 Agent 协作)

多个专业 Agent 协同工作。

```python
from deepagents import create_deep_agent

# 定义专业子代理
coder = {
    "name": "coder",
    "description": "编写代码实现",
    "system_prompt": "你编写干净、经过测试的代码。遵循项目约定。",
}

reviewer = {
    "name": "reviewer",
    "description": "审查代码质量和正确性",
    "system_prompt": "你审查代码中的 bug、风格和正确性。",
}

tester = {
    "name": "tester",
    "description": "编写和运行测试",
    "system_prompt": "你编写全面的测试并运行它们。",
}

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[coder, reviewer, tester],
    system_prompt="""你协调开发工作流：
1. 将编码委派给 coder
2. 将审查委派给 reviewer
3. 将测试委派给 tester
4. 迭代直到全部通过""",
)
```

---

## 示例 9: 异步子代理 (远程部署)

通过 LangSmith 部署的非阻塞子代理。

```python
from deepagents import create_deep_agent, AsyncSubAgent

async_researcher: AsyncSubAgent = {
    "name": "remote-researcher",
    "description": "在远程基础设施上运行长时间研究任务",
    "deployment_url": "https://my-agent.ngrok.langsmith.dev",
}

agent = create_deep_agent(
    model="openai:gpt-5.5",
    async_subagents=[async_researcher],
    system_prompt="将长时间运行的研究委派给 remote-researcher。",
)
```

---

## 示例 10: 组合后端 (读 FS，写内存)

从文件系统读取，写入保留在临时状态中。

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend

backend = CompositeBackend(
    read_backend=FilesystemBackend(root_dir="/workspace"),
    write_backend=StateBackend(),
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=backend,
    system_prompt="读取源文件并将分析写入内存。",
)
```

---

## 示例 11: IoT 智能家居 Agent (SDK 模式)

一个基于 Deep Agents SDK 的智能家居控制 Agent，展示如何用 SDK 构建 IoT 场景。

### 项目结构
```
smart-home-agent/
├── agent.py                  # Agent 工厂函数
├── tools.py                  # 设备控制/环境查询/场景管理工具
├── subagents.yaml            # 子代理定义
├── skills/
│   ├── device-control/SKILL.md
│   └── scene-automation/SKILL.md
└── examples/
    ├── invoke_sync.py
    ├── stream_sync.py
    └── multi_turn.py
```

### Agent 工厂 (agent.py)

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import FilesystemBackend

def create_smart_home_agent(
    model="openai:gpt-5.5",
    checkpointer=None,
):
    chat_model = init_chat_model(model)

    return create_deep_agent(
        model=chat_model,
        tools=[list_devices, control_device, get_environment, trigger_scene, diagnose_device],
        subagents=[
            {
                "name": "device-expert",
                "description": "设备控制与环境监测专家",
                "system_prompt": "你负责控制智能设备、监测环境、执行场景。",
                "tools": [list_devices, control_device, get_environment, trigger_scene],
            },
            {
                "name": "troubleshooter",
                "description": "设备故障排查专家",
                "system_prompt": "你负责诊断设备故障并提供解决方案。",
                "tools": [diagnose_device, list_devices],
            },
        ],
        skills=["./skills/device-control/", "./skills/scene-automation/"],
        memory=["./AGENTS.md"],
        backend=FilesystemBackend(root_dir=".", virtual_mode=True),
        permissions=[
            FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
            FilesystemPermission(operations=["write"], paths=["/data/**"], mode="allow"),
        ],
        checkpointer=checkpointer,
        system_prompt="你是一个智能家居助手，帮用户控制设备、管理场景、排查故障。",
    )
```

### SDK 调用方式

```python
from agent import create_smart_home_agent

# --- 同步调用 ---
agent = create_smart_home_agent()
result = agent.invoke({"messages": "帮我查一下客厅有哪些设备"})
print(result["messages"][-1].content)

# --- 流式输出 ---
for chunk in agent.stream(
    {"messages": "把客厅灯亮度调到50%"},
    stream_mode="values",
):
    last = chunk["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        for tc in last.tool_calls:
            print(f">> {tc['name']}({tc['args']})")
    if last.type == "ai" and last.content:
        print(last.content)

# --- 多轮对话 ---
from langgraph.checkpoint.memory import MemorySaver

agent = create_smart_home_agent(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "home-session"}}

# 第一轮: 查询环境
r1 = await agent.ainvoke({"messages": "客厅温度多少？"}, config=config)
print(r1["messages"][-1].content)  # "当前温度 25.6°C，湿度 58%"

# 第二轮: 基于上文操作 (Agent 记得温度)
r2 = await agent.ainvoke({"messages": "有点热，开空调到24度"}, config=config)
print(r2["messages"][-1].content)  # "已将空调设置为 24°C 制冷模式"

# 第三轮: 场景联动
r3 = await agent.ainvoke({"messages": "我要睡觉了"}, config=config)
print(r3["messages"][-1].content)  # 执行睡眠模式场景

# --- 仅使用工具 (跳过 LLM) ---
from tools import list_devices, control_device

devices = list_devices.invoke({"room": "客厅"})
control_device.invoke({
    "device_name": "客厅灯",
    "action": "set_brightness",
    "params": '{"brightness": 30}',
})
```

### 工具集示例 (tools.py)

```python
from langchain_core.tools import tool

@tool
def list_devices(room: str | None = None) -> str:
    """列出所有已连接的智能设备。可按房间过滤。"""
    # ... 查询设备数据库
    return json.dumps({"devices": [...], "total": 6})

@tool
def control_device(device_name: str, action: str, params: str = "{}") -> str:
    """控制智能设备。支持 on/off/set_brightness/set_temperature 等。"""
    # ... 执行设备控制
    return json.dumps({"success": True, "message": f"已执行: {device_name} -> {action}"})

@tool
def get_environment() -> str:
    """获取家居环境数据（温度、湿度、空气质量）。"""
    return json.dumps({"temperature": 25.6, "humidity": 58, "pm25": 35})

@tool
def trigger_scene(scene_name: str) -> str:
    """执行预设智能场景（回家模式/离家模式/睡眠模式等）。"""
    return json.dumps({"scene": scene_name, "message": f"场景 '{scene_name}' 已执行"})

@tool
def diagnose_device(device_name: str, issue_description: str) -> str:
    """诊断设备故障并给出排查建议。"""
    return json.dumps({"device": device_name, "diagnosis": ["步骤1", "步骤2", ...]})
```

### 技能 SKILL.md 示例

```markdown
---
name: device-control
description: 智能设备控制与状态管理。当用户要求开关设备、调节参数时使用。
---

# 设备控制技能

## 流程
1. 用 list_devices 查看当前状态
2. 用 control_device 执行操作
3. 反馈操作结果

## 支持的操作
| 设备类型 | 操作 |
|---------|------|
| 灯 | on, off, set_brightness (0-100) |
| 空调 | on, off, set_temperature (16-30) |
| 清洁设备 | start_clean, dock |
| 门锁 | lock, unlock (需二次确认) |
```

### 自定义模型

```python
# 使用 DeepSeek
agent = create_smart_home_agent(
    model="openai:deepseek-chat",
)

# 使用 Anthropic
agent = create_smart_home_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
)
```
