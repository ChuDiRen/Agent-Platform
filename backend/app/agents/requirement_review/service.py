"""需求评估服务层"""

from __future__ import annotations

import json
import re

from app.schemas.document import (
    RequirementFinding,
    RequirementReviewRequest,
    RequirementReviewResponse,
)
from app.agents.requirement_review.agent import RequirementReviewAgent

_agent_compiled = None


def _get_agent(**kwargs):
    global _agent_compiled
    if _agent_compiled is None:
        _agent_compiled = RequirementReviewAgent(**kwargs).create()
    return _agent_compiled


def _parse_findings_from_response(content: str) -> list[RequirementFinding]:
    """从 Agent 回复中提取结构化 findings。"""
    code_blocks = re.findall(r"```(?:json)?\s*\n?([\s\S]*?)```", content)
    for block in code_blocks:
        block = block.strip()
        try:
            data = json.loads(block)
            if isinstance(data, list):
                return [RequirementFinding(**f) for f in data]
            if isinstance(data, dict) and "findings" in data:
                return [RequirementFinding(**f) for f in data["findings"]]
        except (json.JSONDecodeError, TypeError):
            continue
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return [RequirementFinding(**f) for f in data]
        if isinstance(data, dict) and "findings" in data:
            return [RequirementFinding(**f) for f in data["findings"]]
    except (json.JSONDecodeError, TypeError):
        pass
    findings: list[RequirementFinding] = []
    blocks = re.split(r"(?=###\s|^\*\*\d+[.、])", content, flags=re.MULTILINE)
    fid = 0
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        title_match = re.match(r"###\s*(.+?)$", block, re.MULTILINE)
        if not title_match:
            title_match = re.match(r"\*\*\d+[.、]\s*(.+?)\*\*", block)
        title = title_match.group(1).strip() if title_match else ""
        if not title:
            continue
        severity = "medium"
        if re.search(r"(严重|高危|high)", block, re.IGNORECASE):
            severity = "high"
        elif re.search(r"(低|建议|low)", block, re.IGNORECASE):
            severity = "low"
        category = "需求评审"
        for cat, kws in {
            "流程完整性": ["流程", "跳转", "状态"],
            "输入校验": ["输入", "校验", "格式"],
            "安全规则": ["安全", "密码", "权限"],
            "异常场景": ["异常", "错误", "超时"],
            "交互细节": ["交互", "按钮", "弹窗"],
        }.items():
            if any(kw in block for kw in kws):
                category = cat
                break
        desc = " ".join(l.strip() for l in block.split("\n")[1:] if l.strip() and not l.startswith("#"))
        findings.append(RequirementFinding(
            id=f"finding-{fid}", title=title[:200], description=(desc or block)[:500],
            severity=severity, category=category, adopted=True,
        ))
        fid += 1
    return findings


def _build_prompt(payload: RequirementReviewRequest) -> str:
    prompt = "请评估以下需求文档，找出所有问题。\n\n"
    prompt += f"## 文档标题\n{payload.title or '未命名'}\n\n"
    prompt += f"## 文档内容\n{payload.content}\n"
    if payload.extra_prompt:
        prompt += f"\n## 补充要求\n{payload.extra_prompt}\n"
    prompt += "\n## 输出要求\n以 JSON 数组返回，每项含 id/title/description/severity/category。\n只输出 JSON。"
    return prompt


def _to_response(payload, content):
    findings = _parse_findings_from_response(content)
    if not findings:
        findings = [RequirementFinding(
            id="ai-evaluation", title="AI 评估结果",
            description=content[:500], severity="medium", category="AI 评估", adopted=True,
        )]
    return RequirementReviewResponse(
        document_id=payload.document_id, title=payload.title, findings=findings,
    )


def _fallback_review(payload: RequirementReviewRequest, error: Exception | None = None) -> RequirementReviewResponse:
    content = payload.content or ""
    findings: list[RequirementFinding] = []
    checks = [
        ("acceptance-criteria", "补充验收标准", "需求中缺少可验证的验收标准，建议明确成功/失败判定。", "medium", ["验收", "标准", "判定"]),
        ("error-handling", "补充异常场景", "需求中缺少失败、超时、重复提交等异常处理说明。", "medium", ["失败", "错误", "异常", "超时"]),
        ("permission-rule", "明确权限规则", "需求中缺少角色、权限或数据访问边界说明。", "low", ["权限", "角色", "管理员"]),
    ]
    for finding_id, title, description, severity, keywords in checks:
        if not any(keyword in content for keyword in keywords):
            findings.append(RequirementFinding(
                id=finding_id,
                title=title,
                description=description,
                severity=severity,
                category="本地规则评审",
                adopted=True,
            ))
    if error is not None:
        findings.append(RequirementFinding(
            id="model-fallback",
            title="已使用本地规则评审",
            description=f"模型服务不可用，已回退到本地规则评审：{error}",
            severity="low",
            category="运行状态",
            adopted=True,
        ))
    if not findings:
        findings.append(RequirementFinding(
            id="basic-review-pass",
            title="基础需求结构完整",
            description="需求包含基础业务描述，未发现阻断性缺口。",
            severity="low",
            category="本地规则评审",
            adopted=True,
        ))
    return RequirementReviewResponse(document_id=payload.document_id, title=payload.title, findings=findings)


def review_requirement(payload: RequirementReviewRequest, **agent_kwargs) -> RequirementReviewResponse:
    try:
        agent = _get_agent(**agent_kwargs)
        result = agent.invoke({"messages": _build_prompt(payload)})
        content = result["messages"][-1].content if hasattr(result["messages"][-1], "content") else ""
        return _to_response(payload, content)
    except Exception as exc:
        return _fallback_review(payload, exc)


async def areview_requirement(payload: RequirementReviewRequest, **agent_kwargs) -> RequirementReviewResponse:
    agent = _get_agent(**agent_kwargs)
    result = await agent.ainvoke({"messages": _build_prompt(payload)})
    content = result["messages"][-1].content if hasattr(result["messages"][-1], "content") else ""
    return _to_response(payload, content)


async def stream_review_requirement(payload: RequirementReviewRequest, **agent_kwargs):
    agent = _get_agent(**agent_kwargs)
    tool_calls_seen = 0
    async for chunk in agent.astream({"messages": _build_prompt(payload)}, stream_mode="values"):
        if "messages" not in chunk:
            continue
        last = chunk["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            for tc in last.tool_calls[tool_calls_seen:]:
                yield {"type": "tool_call", "tool": tc.get("name", ""), "args": tc.get("args", {})}
            tool_calls_seen = len(last.tool_calls)
        if hasattr(last, "content") and last.content and last.type == "ai":
            if not getattr(last, "tool_calls", None):
                findings = _parse_findings_from_response(last.content)
                if not findings:
                    findings = [RequirementFinding(
                        id="ai-evaluation", title="AI 评估结果",
                        description=last.content[:500], severity="medium", category="AI 评估", adopted=True,
                    )]
                yield {"type": "result", "findings": [f.model_dump() for f in findings]}
