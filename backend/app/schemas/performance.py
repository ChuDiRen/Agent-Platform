from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class PerformanceMetric(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    value: float
    unit: str = Field(default="", max_length=32)
    threshold: Optional[float] = None


class PerformanceFinding(BaseModel):
    title: str
    severity: str = "medium"
    description: str
    suggestion: str


class PerformanceAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    summary: str
    findings: list[PerformanceFinding] = Field(default_factory=list)
    trends: list[str] = Field(default_factory=list)


class PerformanceConfigs(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source: str = Field(default="manual", max_length=64)
    scenario: str = Field(default="", max_length=255)
    raw_text: str = Field(default="", max_length=8000)
    metrics: list[PerformanceMetric] = Field(default_factory=list)
    analysis: Optional[PerformanceAnalysis] = None


class PerformanceCreate(BaseModel):
    project_id: Optional[int] = None
    configs: PerformanceConfigs


class PerformanceUpdate(BaseModel):
    project_id: Optional[int] = None
    configs: Optional[PerformanceConfigs] = None


class PerformanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: Optional[int] = None
    configs: PerformanceConfigs
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PerformanceAnalyzeRequest(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    scenario: str = Field(default="", max_length=255)
    raw_text: str = Field(default="", max_length=8000)
    metrics: list[PerformanceMetric] = Field(default_factory=list)


class PerformanceAnalyzeResponse(BaseModel):
    record: PerformanceOut
    analysis: PerformanceAnalysis
    elapsed_ms: int
