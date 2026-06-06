from datetime import datetime
from typing import Any, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ApiRequestDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str
    method: str = "POST"
    url_params: dict[str, Any] = Field(default_factory=dict)
    form: dict[str, Any] = Field(default_factory=dict)
    body_json: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("json", "body_json"),
        serialization_alias="json",
    )
    cookies: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, Any] = Field(default_factory=dict)


class ApiAutomationCase(BaseModel):
    id: int
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    module_name: str
    exec_type: str = "HTTP 请求"
    priority: int = Field(ge=1, le=5)
    name: str
    request: ApiRequestDetails
    expected: str
    created_at: Optional[datetime] = None


class ApiAutomationCaseQuery(BaseModel):
    project_id: Optional[int] = None
    name: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    module_id: Optional[int] = None
    exec_type: Optional[str] = None


class ApiExecutionResult(BaseModel):
    case_id: int
    case_name: str
    status: str
    expected: str
    ai_record: str
    response: dict[str, Any]
    request: ApiRequestDetails


class ApiExecutionDetails(BaseModel):
    summary: dict[str, int]
    results: list[ApiExecutionResult]


class ApiTestExecBase(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    exec_type: str = Field(default="HTTP 请求", max_length=255)
    case_ids: list[int] = Field(min_length=1)
    details: Optional[ApiExecutionDetails] = None
    desc: Optional[str] = Field(default=None, max_length=1024)
    exec_param: dict[str, Any] = Field(default_factory=dict)
    exec_status: str = Field(default="已完成", max_length=255)


class ApiTestExecCreate(ApiTestExecBase):
    pass


class ApiTestExecUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    exec_status: Optional[str] = Field(default=None, max_length=255)
    details: Optional[ApiExecutionDetails] = None
    desc: Optional[str] = Field(default=None, max_length=1024)
    exec_param: Optional[dict[str, Any]] = None


class ApiTestExecOut(ApiTestExecBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApiTestExecRunRequest(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    exec_type: str = Field(default="HTTP 请求", max_length=255)
    case_ids: list[int] = Field(min_length=1)
    exec_param: dict[str, Any] = Field(default_factory=dict)
    desc: Optional[str] = Field(default=None, max_length=1024)
