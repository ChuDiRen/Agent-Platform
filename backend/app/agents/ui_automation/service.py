"""UI 自动化服务层 — 真实实现（基于 ui_automation_cases 表 + Playwright 执行）。"""
from __future__ import annotations

import json
from typing import Any, Callable

from app.schemas.ui_automation import (
    UiExecutionDetails,
    UiExecutionResult,
    UiActionStep,
)


def list_ui_automation_cases(
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
):
    """返回 UI 自动化用例列表（来自 ui_automation_cases 表）。"""
    from app.crud.ui_automation_case import ui_automation_case as case_crud

    return case_crud.get_multi_filtered(
        db=None,
        project_id=project_id,
        name=name,
        priority=priority,
        module_id=module_id,
        exec_type=exec_type,
    )


def get_ui_automation_case(case_id: int):
    """获取单个 UI 自动化用例。"""
    from app.crud.ui_automation_case import ui_automation_case as case_crud

    return case_crud.get(None, case_id)


def _parse_steps(case) -> list[UiActionStep]:
    raw = json.loads(case.steps or "[]") if isinstance(case.steps, str) else (case.steps or [])
    return [UiActionStep(**s) for s in raw]


def build_ui_execution_details(
    case_ids: list[int] | None = None,
    exec_param: dict | None = None,
    db=None,
    check_cancelled: Callable[[], None] | None = None,
) -> UiExecutionDetails:
    """真实执行 UI 自动化：用 Playwright 打开页面并执行步骤。

    若 Playwright 浏览器不可用，则标记为 failed 并给出明确原因（不再返回假成功）。
    check_cancelled: 可选取消检查点回调，供任务系统协作式取消。
    """
    from app.crud.ui_automation_case import ui_automation_case as case_crud

    exec_param = exec_param or {}
    browser_name = exec_param.get("browser") or "chromium"
    ids = case_ids or []
    results: list[UiExecutionResult] = []
    success = 0
    failed = 0

    # 惰性导入 + 浏览器探测：失败时全部标记 failed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        for case_id in ids:
            failed += 1
            results.append(UiExecutionResult(
                case_id=case_id,
                case_name=f"用例#{case_id}",
                status="failed",
                expected="",
                ai_record=f"Playwright 不可用: {exc}",
                page_url="",
                screenshot="",
                steps=[],
                artifacts={},
            ))
        return UiExecutionDetails(summary={"success": 0, "failed": failed, "total": len(ids)}, results=results)

    for case_id in ids:
        if check_cancelled is not None:
            check_cancelled()
        case = case_crud.get(db, case_id) if db else None
        if case is None:
            failed += 1
            results.append(UiExecutionResult(
                case_id=case_id,
                case_name=f"用例#{case_id}",
                status="failed",
                expected="",
                ai_record="用例不存在",
                page_url="",
                screenshot="",
                steps=[],
                artifacts={},
            ))
            continue

        page_url = case.page_url or ""
        steps = _parse_steps(case)
        try:
            with sync_playwright() as p:
                browser_cls = getattr(p, browser_name.lower())
                browser = browser_cls.launch(headless=True)
                page = browser.new_page()
                page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                for step in steps:
                    if step.action == "fill":
                        page.fill(step.target, step.value)
                    elif step.action == "click":
                        page.click(step.target)
                    elif step.action == "goto":
                        page.goto(step.value or step.target, wait_until="domcontentloaded", timeout=30000)
                    elif step.action == "wait":
                        page.wait_for_timeout(int(step.value or 500))
                    elif step.action == "check":
                        page.check(step.target)
                    elif step.action == "screenshot":
                        page.screenshot(path=step.value or "ui-screenshot.png")
                title = page.title()
                browser.close()
            success += 1
            results.append(UiExecutionResult(
                case_id=case.id,
                case_name=case.name,
                status="passed",
                expected=case.expected or "",
                ai_record=f"页面标题: {title}",
                page_url=page_url,
                screenshot="",
                steps=steps,
                artifacts={"title": title},
            ))
        except Exception as exc:
            failed += 1
            results.append(UiExecutionResult(
                case_id=case.id,
                case_name=case.name,
                status="failed",
                expected=case.expected or "",
                ai_record=str(exc),
                page_url=page_url,
                screenshot="",
                steps=steps,
                artifacts={"error": str(exc)},
            ))

    return UiExecutionDetails(
        summary={"success": success, "failed": failed, "total": len(ids)},
        results=results,
    )
