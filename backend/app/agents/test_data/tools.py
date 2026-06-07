"""测试数据生成工具"""
from __future__ import annotations
import json, random, string
from datetime import datetime, timedelta
from langchain_core.tools import tool


@tool
def generate_test_data(fields: str, count: int = 10, data_type: str = "normal") -> str:
    """根据字段定义生成测试数据。

    Args:
        fields: JSON 数组格式的字段定义，如 '[{"name":"username","type":"string","constraints":"6-20位字母数字"}]'。
        count: 生成行数 (1-100)。
        data_type: 数据类型 — normal(正常)/boundary(边界)/invalid(异常)。
    """
    field_defs = json.loads(fields) if isinstance(fields, str) else fields
    count = min(max(count, 1), 100)
    rows = []

    generators = {
        "string": lambda: "".join(random.choices(string.ascii_lowercase, k=random.randint(6, 12))),
        "email": lambda: f"test_{random.randint(100,999)}@example.com",
        "phone": lambda: f"1{random.choice('3456789')}{random.randint(10000000, 99999999)}",
        "number": lambda: random.randint(1, 9999),
        "date": lambda: (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        "password": lambda: f"Test@{random.randint(1000, 9999)}",
        "boolean": lambda: random.choice([True, False]),
        "url": lambda: f"https://example.com/{random.randint(1, 100)}",
    }

    for _ in range(count):
        row = {}
        for f in field_defs:
            name = f.get("name", "field")
            ftype = f.get("type", "string")
            gen = generators.get(ftype, generators["string"])
            row[name] = gen()
        rows.append(row)

    return json.dumps({"data": rows, "total_rows": len(rows), "data_type": data_type}, ensure_ascii=False, indent=2)


@tool
def generate_boundary_data(field_name: str, field_type: str = "string") -> str:
    """为单个字段生成边界值测试数据。

    Args:
        field_name: 字段名称。
        field_type: 字段类型。
    """
    boundary_map = {
        "string": [
            {"value": "", "label": "空字符串"},
            {"value": "a", "label": "最小长度"},
            {"value": "a" * 255, "label": "最大长度"},
            {"value": "测试<script>", "label": "特殊字符"},
        ],
        "number": [
            {"value": 0, "label": "零"},
            {"value": -1, "label": "负数"},
            {"value": 999999999, "label": "大数"},
        ],
        "email": [
            {"value": "", "label": "空"},
            {"value": "no-at-sign", "label": "无@符号"},
            {"value": "a@b.c", "label": "最短有效"},
        ],
    }
    return json.dumps({"field": field_name, "type": field_type, "boundary_data": boundary_map.get(field_type, boundary_map["string"])}, ensure_ascii=False, indent=2)


@tool
def convert_data_format(data: str, target_format: str = "csv") -> str:
    """将测试数据转换为指定格式。

    Args:
        data: JSON 格式的数据数组。
        target_format: 目标格式 — csv/json/sql。
    """
    rows = json.loads(data) if isinstance(data, str) else data
    if target_format == "csv":
        if not rows:
            return json.dumps({"format": "csv", "content": ""})
        headers = list(rows[0].keys())
        lines = [",".join(headers)]
        for r in rows:
            lines.append(",".join(str(r.get(h, "")) for h in headers))
        return json.dumps({"format": "csv", "content": "\n".join(lines), "rows": len(rows)}, ensure_ascii=False)
    elif target_format == "sql":
        if not rows:
            return json.dumps({"format": "sql", "content": ""})
        table = "test_data"
        headers = list(rows[0].keys())
        cols = ", ".join(headers)
        inserts = []
        for r in rows:
            vals = ", ".join(f"'{r.get(h, '')}'" for h in headers)
            inserts.append(f"INSERT INTO {table} ({cols}) VALUES ({vals});")
        return json.dumps({"format": "sql", "content": "\n".join(inserts), "rows": len(rows)}, ensure_ascii=False)
    return json.dumps({"format": "json", "data": rows, "rows": len(rows)}, ensure_ascii=False)
