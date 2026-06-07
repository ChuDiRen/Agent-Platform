"""AI 性能分析"""
from app.agents.base import BaseAgent
from app.agents.performance.prompts import SYSTEM_PROMPT
from app.agents.performance.tools import analyze_performance, detect_bottlenecks, suggest_optimizations
from app.agents.performance.middleware import PerformanceMiddleware


class PerformanceAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def _build_tools(self):
        return [analyze_performance, detect_bottlenecks, suggest_optimizations]

    def _build_middleware(self):
        return [PerformanceMiddleware()]


def create_performance_agent(**kwargs):
    return PerformanceAgent(**kwargs)
