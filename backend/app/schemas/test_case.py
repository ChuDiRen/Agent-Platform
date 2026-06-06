from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequirementModule(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=4000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("module title cannot be empty")
        return trimmed


class TestCaseBase(BaseModel):
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    priority: int = Field(default=2, ge=1, le=5)
    precondition: Optional[str] = Field(default=None, max_length=1024)
    steps: Optional[str] = None
    expected: Optional[str] = Field(default=None, max_length=1024)


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    precondition: Optional[str] = Field(default=None, max_length=1024)
    steps: Optional[str] = None
    expected: Optional[str] = Field(default=None, max_length=1024)


class TestCaseOut(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TestCaseGenerateRequest(BaseModel):
    project_id: Optional[int] = None
    module: RequirementModule
    extra_requirement: Optional[str] = Field(default=None, max_length=1000)


class TestCaseGenerateResponse(BaseModel):
    cases: list[TestCaseCreate]
    elapsed_ms: int


class TestCaseApplyRequest(BaseModel):
    cases: list[TestCaseCreate] = Field(min_length=1)
