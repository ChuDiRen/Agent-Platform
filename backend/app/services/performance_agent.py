import re
import time

from app.schemas.performance import (
    PerformanceAnalysis,
    PerformanceAnalyzeRequest,
    PerformanceFinding,
    PerformanceMetric,
)


DEFAULT_METRICS = [
    PerformanceMetric(name="平均响应时间", value=842, unit="ms", threshold=500),
    PerformanceMetric(name="P95响应时间", value=1680, unit="ms", threshold=1200),
    PerformanceMetric(name="错误率", value=2.8, unit="%", threshold=1),
    PerformanceMetric(name="吞吐量", value=186, unit="req/s", threshold=220),
    PerformanceMetric(name="CPU使用率", value=76, unit="%", threshold=80),
]


def _extract_metrics(raw_text: str) -> list[PerformanceMetric]:
    metrics: list[PerformanceMetric] = []
    patterns = [
        ("平均响应时间", r"(?:平均响应时间|avg|average)[^\d]*(\d+(?:\.\d+)?)", "ms", 500),
        ("P95响应时间", r"(?:p95|P95)[^\d]*(\d+(?:\.\d+)?)", "ms", 1200),
        ("错误率", r"(?:错误率|error)[^\d]*(\d+(?:\.\d+)?)", "%", 1),
        ("吞吐量", r"(?:吞吐量|throughput|tps|qps)[^\d]*(\d+(?:\.\d+)?)", "req/s", 220),
        ("CPU使用率", r"(?:CPU|cpu)[^\d]*(\d+(?:\.\d+)?)", "%", 80),
    ]
    for name, pattern, unit, threshold in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            metrics.append(PerformanceMetric(name=name, value=float(match.group(1)), unit=unit, threshold=threshold))
    return metrics


def analyze_performance(payload: PerformanceAnalyzeRequest) -> tuple[list[PerformanceMetric], PerformanceAnalysis, int]:
    started = time.perf_counter()
    metrics = payload.metrics or _extract_metrics(payload.raw_text) or DEFAULT_METRICS
    findings: list[PerformanceFinding] = []
    penalty = 0

    for metric in metrics:
        if metric.threshold is None:
            continue
        over_limit = metric.name != "吞吐量" and metric.value > metric.threshold
        under_limit = metric.name == "吞吐量" and metric.value < metric.threshold
        if not (over_limit or under_limit):
            continue
        gap = abs(metric.value - metric.threshold)
        severity = "high" if gap / max(metric.threshold, 1) > 0.35 else "medium"
        penalty += 18 if severity == "high" else 10
        findings.append(
            PerformanceFinding(
                title=f"{metric.name}未达标",
                severity=severity,
                description=f"{metric.name}为{metric.value:g}{metric.unit}，基线为{metric.threshold:g}{metric.unit}。",
                suggestion="建议定位慢接口、检查数据库索引与缓存命中率，并结合压测时段的资源曲线复核容量瓶颈。",
            )
        )

    if not findings:
        findings.append(
            PerformanceFinding(
                title="性能指标整体达标",
                severity="low",
                description="关键性能指标均处于当前阈值范围内。",
                suggestion="建议保留本次基线，后续发布前复用相同场景做回归对比。",
            )
        )

    score = max(0, 100 - penalty)
    summary = (
        f"AI已分析{payload.scenario or payload.name}，发现{len([item for item in findings if item.severity != 'low'])}个需要关注的性能风险。"
        if score < 90
        else f"AI已分析{payload.scenario or payload.name}，当前性能表现稳定。"
    )
    analysis = PerformanceAnalysis(
        score=score,
        summary=summary,
        findings=findings,
        trends=[
            "响应时间峰值主要集中在登录后首屏和列表查询阶段。",
            "吞吐能力与CPU曲线存在相关性，建议扩展并发阶段继续观察。",
            "错误率若持续超过1%，需要优先排查超时和连接池耗尽。", 
        ],
    )
    elapsed_ms = max(1, int((time.perf_counter() - started) * 1000))
    return metrics, analysis, elapsed_ms
