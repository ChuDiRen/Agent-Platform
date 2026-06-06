from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class UiActionStep(BaseModel):
    action: str
    target: str
    value: str = ""


class UiAutomationCase(BaseModel):
    id: int
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    module_name: str
    exec_type: str = "WEB 网页"
    priority: int = Field(ge=1, le=5)
    name: str
    page_url: str
    viewport: str = "desktop"
    steps: list[UiActionStep] = Field(default_factory=list)
    expected: str
    created_at: Optional[datetime] = None


class UiExecutionResult(BaseModel):
    case_id: int
    case_name: str
    status: str
    expected: str
    ai_record: str
    page_url: str
    screenshot: str
    steps: list[UiActionStep]
    artifacts: dict[str, Any] = Field(default_factory=dict)


class UiExecutionDetails(BaseModel):
    summary: dict[str, int]
    results: list[UiExecutionResult]


class UiTestExecBase(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    exec_type: str = Field(default="WEB 网页", max_length=255)
    case_ids: list[int] = Field(min_length=1)
    details: Optional[UiExecutionDetails] = None
    desc: Optional[str] = Field(default=None, max_length=1024)
    exec_param: dict[str, Any] = Field(default_factory=dict)
    exec_status: str = Field(default="已完成", max_length=255)


class UiTestExecCreate(UiTestExecBase):
    pass


class UiTestExecUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    exec_status: Optional[str] = Field(default=None, max_length=255)
    details: Optional[UiExecutionDetails] = None
    desc: Optional[str] = Field(default=None, max_length=1024)
    exec_param: Optional[dict[str, Any]] = None


class UiTestExecOut(UiTestExecBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UiTestExecRunRequest(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    exec_type: str = Field(default="WEB 网页", max_length=255)
    case_ids: list[int] = Field(min_length=1)
    exec_param: dict[str, Any] = Field(default_factory=dict)
    desc: Optional[str] = Field(default=None, max_length=1024)
