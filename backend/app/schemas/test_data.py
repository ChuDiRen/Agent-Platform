from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


FieldType = Literal["number", "string", "email", "phone", "date", "boolean"]
OutputFormat = Literal["json", "csv"]
Language = Literal["zh", "en"]


class TestDataField(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    type: FieldType = "string"
    rule: str = Field(default="", max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("field name cannot be empty")
        return trimmed


class TestDataTemplateBase(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    fields: list[TestDataField] = Field(default_factory=list, min_length=1)
    hint: Optional[str] = Field(default=None, max_length=1000)
    count: int = Field(default=10, ge=1, le=500)
    format: OutputFormat = "json"
    lang: Language = "zh"


class TestDataTemplateCreate(TestDataTemplateBase):
    pass


class TestDataTemplateUpdate(BaseModel):
    project_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    fields: Optional[list[TestDataField]] = Field(default=None, min_length=1)
    hint: Optional[str] = Field(default=None, max_length=1000)
    count: Optional[int] = Field(default=None, ge=1, le=500)
    format: Optional[OutputFormat] = None
    lang: Optional[Language] = None


class TestDataTemplateOut(TestDataTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TestDataGenerateRequest(BaseModel):
    fields: list[TestDataField] = Field(default_factory=list, min_length=1)
    hint: Optional[str] = Field(default=None, max_length=1000)
    count: int = Field(default=10, ge=1, le=500)
    format: OutputFormat = "json"
    lang: Language = "zh"


class TestDataGenerateResponse(BaseModel):
    data: list[dict[str, Any]]
    content: str
    format: OutputFormat
    count: int
    elapsed_ms: int
