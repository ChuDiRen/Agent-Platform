---
name: ui-automation-script
description: UI 自动化脚本技能。指导 Agent 生成 Playwright 测试脚本，覆盖核心业务流程。
---

# UI 自动化脚本技能

## 框架规范

### Playwright Python 风格
```python
from playwright.sync_api import Page, expect

def test_login_flow(page: Page):
    page.goto("http://localhost:3000/login")
    page.get_by_placeholder("请输入用户名").fill("admin")
    page.get_by_placeholder("请输入密码").fill("admin123")
    page.get_by_role("button", name="登录").click()
    expect(page).to_have_url("**/dashboard")
```

### 选择器优先级
1. `get_by_role` (无障碍角色) — 最稳定
2. `get_by_test_id` (data-testid) — 测试专用
3. `get_by_placeholder` / `get_by_text` — 可读性好
4. CSS 选择器 — 最后手段

### 等待策略
- `page.wait_for_load_state("networkidle")` — 页面加载
- `expect(locator).to_be_visible()` — 元素可见
- `expect(page).to_have_url()` — URL 变化

## 用例模式

### 登录流程
```python
def test_login(page):
    page.goto("/login")
    page.get_by_placeholder("用户名").fill("admin")
    page.get_by_placeholder("密码").fill("123456")
    page.get_by_role("button", name="登录").click()
    expect(page).to_have_url("**/home")
```

### 表单提交
```python
def test_form_submit(page):
    page.goto("/form")
    page.get_by_label("名称").fill("测试")
    page.get_by_role("button", name="提交").click()
    expect(page.get_by_text("提交成功")).to_be_visible()
```

### 列表操作
```python
def test_list_filter(page):
    page.goto("/list")
    page.get_by_placeholder("搜索").fill("关键词")
    page.keyboard.press("Enter")
    expect(page.get_by_test_id("list-item")).to_have_count(1)
```
