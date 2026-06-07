"""性能分析服务层 — 提供给 API 端点使用"""
from app.agents.performance.tools import analyze_performance as _analyze, detect_bottlenecks, suggest_optimizations


def analyze_performance(data: str):
    """分析性能数据。"""
    result = _analyze.invoke({"data": data})
    import json
    return json.loads(result)
