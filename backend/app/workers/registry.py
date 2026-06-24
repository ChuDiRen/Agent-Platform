from __future__ import annotations

from app.workers.executor import AgentExecutor


def _execute_test_data(payload, context):
    from app.schemas.test_data import TestDataGenerateRequest
    from app.agents.test_data.service import generate_test_data_response

    context.emit_event("正在生成测试数据", progress=30)
    result = generate_test_data_response(TestDataGenerateRequest.model_validate(payload))
    return _result("测试数据生成完成", result.model_dump())


def _execute_test_case(payload, context):
    from app.schemas.test_case import TestCaseGenerateRequest
    from app.agents.test_case.service import generate_test_cases

    context.emit_event("正在生成测试用例", progress=30)
    cases, elapsed_ms = generate_test_cases(TestCaseGenerateRequest.model_validate(payload))
    return _result("测试用例生成完成", {"cases": cases, "elapsed_ms": elapsed_ms})


def _execute_requirement_review(payload, context):
    from app.schemas.document import RequirementReviewRequest
    from app.agents.requirement_review.service import review_requirement

    context.emit_event("正在评审需求", progress=30)
    result = review_requirement(RequirementReviewRequest.model_validate(payload))
    return _result("需求评审完成", result.model_dump())


def _execute_api_document(payload, context):
    from app.agents.api_document.service import analyze_api_document

    context.emit_event("正在分析接口文档", progress=30)
    result = analyze_api_document(payload.get("content", ""), payload.get("extra_prompt", ""))
    return _result("接口文档分析完成", result)


def _execute_api_automation(payload, context):
    from app.agents.api_automation.service import build_execution_details
    from app.crud.api_test_cases_exec import api_test_cases_exec
    from app.schemas.api_automation import ApiTestExecCreate

    context.emit_event("正在执行接口自动化", progress=30)
    case_ids = payload.get("case_ids", [])
    details = build_execution_details(case_ids=case_ids, exec_param=payload.get("exec_param", {}))
    if not case_ids:
        return _result("接口自动化执行完成", {"record_id": None, "details": details})
    record = api_test_cases_exec.create(
        context.db,
        obj_in=ApiTestExecCreate(
            project_id=context.project_id,
            name=payload.get("name", "AI接口自动化任务"),
            exec_type=payload.get("exec_type", "HTTP 请求"),
            case_ids=case_ids,
            details=details,
            desc=payload.get("desc"),
            exec_param=payload.get("exec_param", {}),
            exec_status="已完成",
        ),
    )
    return _result("接口自动化执行完成", {"record_id": record.id, "details": details})


def _execute_ui_automation(payload, context):
    from app.agents.ui_automation.service import build_ui_execution_details
    from app.crud.ui_test_cases_exec import ui_test_cases_exec
    from app.schemas.ui_automation import UiTestExecCreate

    context.emit_event("正在执行 UI 自动化", progress=30)
    case_ids = payload.get("case_ids", [])
    details = build_ui_execution_details(case_ids=case_ids, exec_param=payload.get("exec_param", {}))
    if not case_ids:
        return _result("UI 自动化执行完成", {"record_id": None, "details": details})
    record = ui_test_cases_exec.create(
        context.db,
        obj_in=UiTestExecCreate(
            project_id=context.project_id,
            name=payload.get("name", "AI UI自动化任务"),
            exec_type=payload.get("exec_type", "WEB 网页"),
            case_ids=case_ids,
            details=details,
            desc=payload.get("desc"),
            exec_param=payload.get("exec_param", {}),
            exec_status="已完成",
        ),
    )
    return _result("UI 自动化执行完成", {"record_id": record.id, "details": details})


def _execute_performance(payload, context):
    from app.agents.performance.service import analyze_performance
    from app.crud.performance import performance as performance_crud
    from app.schemas.performance import PerformanceConfigs, PerformanceCreate

    context.emit_event("正在分析性能数据", progress=30)
    result = analyze_performance(payload.get("raw_text", "") or str(payload))
    record = performance_crud.create(
        context.db,
        obj_in=PerformanceCreate(
            project_id=context.project_id,
            configs=PerformanceConfigs(
                name=payload.get("name", "性能分析任务"),
                source="ai-analysis",
                scenario=payload.get("scenario", ""),
                raw_text=payload.get("raw_text", ""),
                metrics=payload.get("metrics", []),
                analysis=result.get("analysis") if isinstance(result, dict) else None,
            ),
        ),
    )
    output = result if isinstance(result, dict) else {"analysis": result}
    output["record_id"] = record.id
    return _result("性能分析完成", output)


def _result(summary, output):
    from app.workers.executor import AgentExecutionResult

    return AgentExecutionResult(summary=summary, output=output or {})


EXECUTORS: dict[str, AgentExecutor] = {
    "test_data": _execute_test_data,
    "test_case": _execute_test_case,
    "requirement_review": _execute_requirement_review,
    "api_document": _execute_api_document,
    "api_automation": _execute_api_automation,
    "ui_automation": _execute_ui_automation,
    "performance": _execute_performance,
}


def get_executor(agent_key: str) -> AgentExecutor:
    try:
        return EXECUTORS[agent_key]
    except KeyError as exc:
        raise ValueError(f"Unknown agent_key: {agent_key}") from exc
