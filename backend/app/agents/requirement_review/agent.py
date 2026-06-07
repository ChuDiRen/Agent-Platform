"""AI 需求评估助手"""
from app.agents.base import BaseAgent
from app.agents.requirement_review.prompts import SYSTEM_PROMPT, SUBAGENT_COMPLETENESS, SUBAGENT_CLASSIFIER
from app.agents.requirement_review.tools import (
    assess_severity, categorize_finding, check_completeness, extract_requirements,
)
from app.agents.requirement_review.middleware import RequirementReviewMiddleware


class RequirementReviewAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT
    ENABLE_VALIDATION = True

    def _build_tools(self):
        return [extract_requirements, check_completeness, assess_severity, categorize_finding]

    def _build_subagents(self):
        return [
            {"name": "completeness-checker", "description": "检查需求文档在各维度的完整性",
             "system_prompt": SUBAGENT_COMPLETENESS, "tools": [check_completeness]},
            {"name": "finding-classifier", "description": "对发现的问题进行分类和严重程度评估",
             "system_prompt": SUBAGENT_CLASSIFIER, "tools": [categorize_finding, assess_severity]},
        ]

    def _build_middleware(self):
        return [RequirementReviewMiddleware()]


def create_requirement_review_agent(**kwargs):
    return RequirementReviewAgent(**kwargs)
