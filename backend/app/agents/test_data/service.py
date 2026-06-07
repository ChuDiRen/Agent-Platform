"""测试数据服务层 — 提供给 API 端点使用"""
from app.agents.test_data.tools import generate_test_data, convert_data_format
from app.schemas.test_data import TestDataGenerateResponse
import json, time


def generate_test_data_response(payload):
    """生成测试数据并返回标准响应。"""
    started = time.perf_counter()

    fields_json = json.dumps([f.model_dump() for f in payload.fields]) if hasattr(payload, "fields") else "[]"
    result = generate_test_data.invoke({
        "fields": fields_json,
        "count": getattr(payload, "count", 10),
        "data_type": getattr(payload, "data_type", "normal"),
    })
    data = json.loads(result)

    fmt = getattr(payload, "format", "json")
    convert_result = convert_data_format.invoke({
        "data": json.dumps(data.get("data", [])),
        "target_format": fmt,
    })
    converted = json.loads(convert_result)

    elapsed_ms = max(1, int((time.perf_counter() - started) * 1000))

    return TestDataGenerateResponse(
        content=converted.get("content", ""),
        format=fmt,
        rows=data.get("total_rows", 0),
        elapsed_ms=elapsed_ms,
    )
