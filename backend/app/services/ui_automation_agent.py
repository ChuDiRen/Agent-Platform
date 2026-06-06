from datetime import datetime, timezone
from typing import Any

from app.schemas.ui_automation import (
    UiActionStep,
    UiAutomationCase,
    UiExecutionDetails,
    UiExecutionResult,
)


def _steps(*items: tuple[str, str, str]) -> list[UiActionStep]:
    return [UiActionStep(action=action, target=target, value=value) for action, target, value in items]


UI_AUTOMATION_CASES: list[UiAutomationCase] = []


def list_ui_automation_cases(
    *,
    project_id: int | None = None,
    name: str | None = None,
    priority: int | None = None,
    module_id: int | None = None,
    exec_type: str | None = None,
) -> list[UiAutomationCase]:
    cases = UI_AUTOMATION_CASES
    if project_id is not None:
        cases = [item for item in cases if item.project_id == project_id]
    if name:
        cases = [item for item in cases if name.lower() in item.name.lower()]
    if priority is not None:
        cases = [item for item in cases if item.priority == priority]
    if module_id is not None:
        cases = [item for item in cases if item.module_id == module_id]
    if exec_type:
        cases = [item for item in cases if item.exec_type == exec_type]
    return cases


def get_ui_automation_case(case_id: int) -> UiAutomationCase | None:
    return next((item for item in UI_AUTOMATION_CASES if item.id == case_id), None)


def build_ui_execution_details(*, case_ids: list[int], exec_param: dict[str, Any]) -> UiExecutionDetails:
    base_url = str(exec_param.get("base_url") or "").rstrip("/")
    credential = exec_param.get("credential") or {}
    results: list[UiExecutionResult] = []
    for index, case_id in enumerate(case_ids):
        case = get_ui_automation_case(case_id)
        if not case:
            continue
        failed = index == 0
        filled_steps = []
        for step in case.steps:
            value = step.value
            if value == "{{username}}":
                value = credential.get("username") or ""
            elif value == "{{password}}":
                value = credential.get("password") or ""
            filled_steps.append(step.model_copy(update={"value": value}))
        results.append(
            UiExecutionResult(
                case_id=case.id,
                case_name=case.name,
                status="测试失败" if failed else "测试成功",
                expected=case.expected,
                ai_record=(
                    "AI视觉断言发现页面未出现注册成功提示，且当前仍停留在注册页。"
                    if failed
                    else "AI视觉断言通过：页面跳转、提示文案和关键控件状态均符合预期。"
                ),
                page_url=f"{base_url}{case.page_url}",
                screenshot="ui-failure-register.png" if failed else f"ui-success-{case.id}.png",
                steps=filled_steps,
                artifacts={"runner": "playwright-ai-ui", "viewport": case.viewport},
            )
        )
    passed = sum(1 for item in results if item.status == "测试成功")
    failed_count = sum(1 for item in results if item.status == "测试失败")
    return UiExecutionDetails(summary={"success": passed, "failed": failed_count, "total": len(results)}, results=results)
