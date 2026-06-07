"""AI 需求评估助手 — 工具集

为需求评估 Agent 提供结构化分析工具。
所有工具基于 Deep Agents SDK 的 @tool 装饰器。
"""

from __future__ import annotations

import json
import re
from typing import Literal

from langchain_core.tools import tool


@tool
def extract_requirements(content: str) -> str:
    """从需求文档中提取结构化需求条目。识别功能点、用户故事、业务规则等。

    Args:
        content: 需求文档原文。
    """
    findings: list[dict] = []

    # 按段落拆分，识别潜在需求条目
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", content) if p.strip()]

    for i, para in enumerate(paragraphs):
        # 跳过标题行和空段
        if re.match(r"^#{1,6}\s", para) and len(para) < 200:
            continue

        entry: dict = {
            "index": i,
            "text": para[:500],
            "type": "unknown",
            "has_acceptance_criteria": False,
            "has_edge_cases": False,
            "ambiguity_signals": [],
        }

        lower = para.lower()

        # 分类
        if any(kw in lower for kw in ["用户可以", "用户能够", "作为用户", "角色"]):
            entry["type"] = "user_story"
        elif any(kw in lower for kw in ["规则", "必须", "应当", "不允许", "限制"]):
            entry["type"] = "business_rule"
        elif any(kw in lower for kw in ["接口", "api", "请求", "响应", "参数"]):
            entry["type"] = "api_spec"
        elif any(kw in lower for kw in ["页面", "界面", "按钮", "输入框", "弹窗"]):
            entry["type"] = "ui_spec"
        elif any(kw in lower for kw in ["流程", "步骤", "首先", "然后", "最后"]):
            entry["type"] = "flow"
        else:
            entry["type"] = "general"

        # 验收标准检测
        if any(kw in lower for kw in ["验收", "标准", "预期", "成功时", "失败时"]):
            entry["has_acceptance_criteria"] = True

        # 边界场景检测
        if any(kw in lower for kw in ["异常", "错误", "失败", "超时", "边界", "为空", "非法"]):
            entry["has_edge_cases"] = True

        # 模糊信号检测
        ambiguity = []
        if any(kw in lower for kw in ["等", "等等", "之类的", "大概", "可能", "或许"]):
            ambiguity.append("含模糊限定词")
        if re.search(r"[^\x00-\x7F]{0,5}(未指定|未定义|未说明|待定|TBD|TODO)", para, re.IGNORECASE):
            ambiguity.append("存在待定项")
        if len(para) > 300 and not entry["has_acceptance_criteria"]:
            ambiguity.append("长段落但无验收标准")
        entry["ambiguity_signals"] = ambiguity

        findings.append(entry)

    return json.dumps({
        "total_paragraphs": len(paragraphs),
        "extracted_requirements": findings,
        "summary": {
            "user_stories": sum(1 for f in findings if f["type"] == "user_story"),
            "business_rules": sum(1 for f in findings if f["type"] == "business_rule"),
            "api_specs": sum(1 for f in findings if f["type"] == "api_spec"),
            "ui_specs": sum(1 for f in findings if f["type"] == "ui_spec"),
            "flows": sum(1 for f in findings if f["type"] == "flow"),
            "with_acceptance_criteria": sum(1 for f in findings if f["has_acceptance_criteria"]),
            "with_edge_cases": sum(1 for f in findings if f["has_edge_cases"]),
            "with_ambiguity": sum(1 for f in findings if f["ambiguity_signals"]),
        },
    }, ensure_ascii=False, indent=2)


@tool
def check_completeness(
    content: str,
    aspect: Literal["flow", "input_validation", "security", "error_handling", "permissions", "all"] = "all",
) -> str:
    """检查需求文档在指定维度的完整性。找出缺失或不清晰的部分。

    Args:
        content: 需求文档原文。
        aspect: 检查维度 — flow(流程)/input_validation(输入校验)/security(安全)/error_handling(异常处理)/permissions(权限)/all(全部)。
    """
    checks: list[dict] = []

    dimensions = {
        "flow": {
            "name": "流程完整性",
            "keywords": ["跳转", "重定向", "成功", "失败", "下一步", "返回", "流程"],
            "missing_hints": ["登录后跳转", "操作成功反馈", "取消操作流程", "返回上级"],
        },
        "input_validation": {
            "name": "输入校验",
            "keywords": ["格式", "长度", "类型", "必填", "正则", "校验", "验证", "限制"],
            "missing_hints": ["输入框格式要求", "长度限制", "特殊字符处理", "必填项标识"],
        },
        "security": {
            "name": "安全规则",
            "keywords": ["密码", "加密", "token", "权限", "鉴权", "会话", "安全"],
            "missing_hints": ["密码复杂度", "会话超时", "登录失败锁定", "敏感数据脱敏"],
        },
        "error_handling": {
            "name": "异常处理",
            "keywords": ["异常", "错误", "失败", "超时", "重试", "回退", "提示"],
            "missing_hints": ["网络异常处理", "服务端错误提示", "操作超时处理", "并发冲突处理"],
        },
        "permissions": {
            "name": "权限控制",
            "keywords": ["角色", "权限", "管理员", "普通用户", "访问控制", "可见"],
            "missing_hints": ["角色定义", "权限边界", "越权防护", "数据隔离"],
        },
    }

    aspects_to_check = {k: v for k, v in dimensions.items()} if aspect == "all" else {aspect: dimensions[aspect]}

    for dim_key, dim in aspects_to_check.items():
        lower = content.lower()
        found = [kw for kw in dim["keywords"] if kw in lower]
        coverage = len(found) / len(dim["keywords"]) if dim["keywords"] else 0

        severity = "low"
        if coverage < 0.15:
            severity = "high"
        elif coverage < 0.35:
            severity = "medium"

        if severity != "low":
            checks.append({
                "dimension": dim["name"],
                "dimension_key": dim_key,
                "coverage": f"{coverage:.0%}",
                "severity": severity,
                "found_keywords": found[:5],
                "suggestions": dim["missing_hints"],
            })

    return json.dumps({
        "aspect_checked": aspect,
        "total_dimensions": len(aspects_to_check),
        "issues_found": len(checks),
        "issues": checks,
    }, ensure_ascii=False, indent=2)


@tool
def assess_severity(
    title: str,
    description: str,
    category: str,
) -> str:
    """评估单个需求问题的严重程度 (high/medium/low)。

    Args:
        title: 问题标题。
        description: 问题描述。
        category: 问题类别 (如 流程完整性、输入校验、安全规则、异常场景、交互细节)。
    """
    severity_score = 0
    combined = f"{title} {description} {category}".lower()

    # 高危信号
    high_signals = ["安全", "数据丢失", "权限", "注入", "泄露", "支付", "密码", "锁死", "无法恢复"]
    for sig in high_signals:
        if sig in combined:
            severity_score += 3

    # 中危信号
    medium_signals = ["校验", "格式", "提示", "异常", "失败", "超时", "重复", "兼容"]
    for sig in medium_signals:
        if sig in combined:
            severity_score += 2

    # 低危信号
    low_signals = ["样式", "文案", "颜色", "间距", "对齐", "动效", "提示语"]
    for sig in low_signals:
        if sig in combined:
            severity_score += 1

    if severity_score >= 6:
        level = "high"
    elif severity_score >= 3:
        level = "medium"
    else:
        level = "low"

    return json.dumps({
        "title": title,
        "category": category,
        "severity": level,
        "score": severity_score,
        "rationale": f"基于类别 '{category}' 和内容关键词分析，综合评分 {severity_score}。",
    }, ensure_ascii=False, indent=2)


@tool
def categorize_finding(
    title: str,
    description: str,
) -> str:
    """将需求问题自动分类到最匹配的类别。

    Args:
        title: 问题标题。
        description: 问题描述。
    """
    combined = f"{title} {description}".lower()

    categories = {
        "流程完整性": ["流程", "跳转", "顺序", "步骤", "状态", "流转"],
        "输入校验": ["输入", "格式", "长度", "类型", "校验", "必填", "正则"],
        "安全规则": ["安全", "密码", "权限", "加密", "token", "鉴权"],
        "异常场景": ["异常", "错误", "失败", "超时", "重试", "边界"],
        "交互细节": ["交互", "按钮", "弹窗", "提示", "反馈", "加载"],
        "数据一致性": ["数据", "同步", "缓存", "并发", "一致性"],
        "性能要求": ["性能", "响应时间", "并发", "容量", "延迟"],
        "兼容性": ["兼容", "浏览器", "设备", "分辨率", "版本"],
    }

    scores: dict[str, int] = {}
    for cat, keywords in categories.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            scores[cat] = score

    if not scores:
        best = "需求评审"
        confidence = 0.0
    else:
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        total = sum(scores.values())
        confidence = scores[best] / total if total > 0 else 0

    return json.dumps({
        "category": best,
        "confidence": round(confidence, 2),
        "candidates": scores,
    }, ensure_ascii=False, indent=2)
