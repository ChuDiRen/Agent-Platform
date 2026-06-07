"""智能体模块

所有基于 Deep Agents SDK 的 AI 智能体统一存放于此。
每个智能体是独立目录，包含 agent.py / tools.py / 可选的 subagents.yaml。

目录结构:
    app/agents/
    ├── base.py                    # BaseAgent 基类
    ├── requirement_review/        # ① AI 需求评估助手
    ├── test_case/                 # ② AI 测试用例智能体
    ├── ui_automation/             # ③ AI 界面 UI 自动化
    ├── api_document/              # ④ AI 接口文档分析
    ├── api_test_case/             # ⑤ AI 接口用例设计
    ├── api_automation/            # ⑥ AI 接口自动化脚本
    ├── test_data/                 # ⑦ AI 测试数据生成
    └── performance/               # ⑧ AI 性能数据分析

用法:
    from app.agents.requirement_review import RequirementReviewAgent
    agent = RequirementReviewAgent().create()
    result = agent.invoke({"messages": "..."})
"""
