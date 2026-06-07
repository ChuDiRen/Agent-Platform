"""性能分析工具"""
from __future__ import annotations
import json
from langchain_core.tools import tool


@tool
def analyze_performance(data: str) -> str:
    """分析性能测试数据，提取关键指标。

    Args:
        data: JSON 格式的性能测试结果（含 response_time, throughput, error_rate 等）。
    """
    try:
        metrics = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, TypeError):
        metrics = {}

    response_times = metrics.get("response_times", [])
    error_count = metrics.get("error_count", 0)
    total_requests = metrics.get("total_requests", 1)

    avg_rt = sum(response_times) / len(response_times) if response_times else 0
    p95 = sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
    error_rate = error_count / total_requests if total_requests > 0 else 0

    summary = {
        "avg_response_time_ms": round(avg_rt, 2),
        "p95_response_time_ms": round(p95, 2),
        "error_rate": f"{error_rate:.2%}",
        "total_requests": total_requests,
        "status": "PASS" if avg_rt < 2000 and error_rate < 0.01 else "FAIL",
    }

    return json.dumps(summary, ensure_ascii=False, indent=2)


@tool
def detect_bottlenecks(metrics: str) -> str:
    """检测性能瓶颈。

    Args:
        metrics: JSON 格式的性能指标数据。
    """
    try:
        data = json.loads(metrics) if isinstance(metrics, str) else metrics
    except (json.JSONDecodeError, TypeError):
        data = {}

    bottlenecks = []

    avg_rt = data.get("avg_response_time_ms", 0)
    if avg_rt > 3000:
        bottlenecks.append({"area": "响应时间", "severity": "high", "detail": f"平均响应时间 {avg_rt}ms 超过 3s 阈值"})
    elif avg_rt > 1000:
        bottlenecks.append({"area": "响应时间", "severity": "medium", "detail": f"平均响应时间 {avg_rt}ms，建议优化至 1s 内"})

    error_rate = data.get("error_rate", "0%")
    if isinstance(error_rate, str):
        error_rate = float(error_rate.strip("%")) / 100
    if error_rate > 0.05:
        bottlenecks.append({"area": "错误率", "severity": "high", "detail": f"错误率 {error_rate:.2%} 超过 5%"})

    cpu = data.get("cpu_usage_percent", 0)
    if cpu > 80:
        bottlenecks.append({"area": "CPU", "severity": "high", "detail": f"CPU 使用率 {cpu}% 超过 80%"})

    memory = data.get("memory_usage_percent", 0)
    if memory > 85:
        bottlenecks.append({"area": "内存", "severity": "high", "detail": f"内存使用率 {memory}% 超过 85%"})

    return json.dumps({"bottlenecks": bottlenecks, "total": len(bottlenecks)}, ensure_ascii=False, indent=2)


@tool
def suggest_optimizations(bottlenecks: str) -> str:
    """根据瓶颈给出优化建议。

    Args:
        bottlenecks: JSON 格式的瓶颈列表。
    """
    try:
        data = json.loads(bottlenecks) if isinstance(bottlenecks, str) else bottlenecks
    except (json.JSONDecodeError, TypeError):
        data = {"bottlenecks": []}

    suggestion_map = {
        "响应时间": ["添加 Redis 缓存热点数据", "优化数据库查询，添加索引", "启用 CDN 加速静态资源", "考虑异步处理非关键路径"],
        "错误率": ["检查服务端异常日志", "增加请求重试机制", "检查依赖服务健康状态", "添加熔断降级策略"],
        "CPU": ["优化算法复杂度", "减少不必要的计算", "考虑水平扩展", "检查是否有死循环或密集计算"],
        "内存": ["检查是否有内存泄漏", "优化数据结构，减少大对象", "增加 JVM 堆内存或容器资源", "检查缓存策略是否有淘汰机制"],
    }

    suggestions = []
    for b in data.get("bottlenecks", []):
        area = b.get("area", "")
        for s in suggestion_map.get(area, []):
            suggestions.append({"area": area, "suggestion": s, "priority": b.get("severity", "medium")})

    return json.dumps({"suggestions": suggestions, "total": len(suggestions)}, ensure_ascii=False, indent=2)
