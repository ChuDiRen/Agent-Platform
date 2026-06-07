"""UI 自动化工具"""
from __future__ import annotations
import json
from langchain_core.tools import tool


@tool
def generate_ui_script(steps: str, url: str = "http://localhost:3000") -> str:
    """根据操作步骤生成 Playwright 测试脚本。

    Args:
        steps: 操作步骤描述（自然语言）。
        url: 目标页面 URL。
    """
    script = f'''import pytest
from playwright.sync_api import Page, expect


def test_ui_flow(page: Page):
    """UI 自动化测试"""
    # 导航
    page.goto("{url}")
    page.wait_for_load_state("networkidle")

    # TODO: 根据步骤描述生成具体操作
    # {steps}

    # 断言页面加载完成
    expect(page).not_to_have_url("about:blank")
'''
    return json.dumps({"script": script, "url": url}, ensure_ascii=False, indent=2)


@tool
def analyze_page_elements(html: str) -> str:
    """分析 HTML 内容，识别可交互的页面元素。

    Args:
        html: 页面 HTML 内容。
    """
    import re
    elements = []
    # 提取 input
    for m in re.finditer(r'<input[^>]*?(?:id|name|placeholder)=["\']([^"\']*)["\']', html):
        elements.append({"type": "input", "identifier": m.group(1)})
    # 提取 button
    for m in re.finditer(r'<button[^>]*?(?:id|class)=["\']([^"\']*)["\']', html):
        elements.append({"type": "button", "identifier": m.group(1)})
    # 提取 a
    for m in re.finditer(r'<a[^>]*?href=["\']([^"\']*)["\']', html):
        elements.append({"type": "link", "identifier": m.group(1)})
    return json.dumps({"elements": elements[:20], "total": len(elements)}, ensure_ascii=False, indent=2)


@tool
def suggest_selectors(element_type: str, attributes: str = "{}") -> str:
    """为页面元素推荐稳定的选择器策略。

    Args:
        element_type: 元素类型 (input/button/link/div)。
        attributes: 元素属性 JSON，如 '{"id":"login-btn","class":"btn-primary","text":"登录"}'。
    """
    attrs = json.loads(attributes) if isinstance(attributes, str) else attributes
    selectors = []
    if "id" in attrs:
        selectors.append({"selector": f"#{attrs['id']}", "priority": 1, "reason": "ID 选择器最稳定"})
    if "text" in attrs:
        selectors.append({"selector": f"text={attrs['text']}", "priority": 2, "reason": "文本选择器易读"})
    if "data-testid" in attrs:
        selectors.append({"selector": f"[data-testid={attrs['data-testid']}]", "priority": 1, "reason": "测试专用属性"})
    if "class" in attrs:
        selectors.append({"selector": f".{attrs['class'].split()[0]}", "priority": 3, "reason": "Class 选择器可能变化"})
    return json.dumps({"selectors": selectors}, ensure_ascii=False, indent=2)
