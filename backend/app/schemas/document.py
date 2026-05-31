from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Severity = Literal["high", "medium", "low"]


class RequirementFinding(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity = "medium"
    category: str = "需求评审"
    adopted: bool = False


class DocumentBase(BaseModel):
    project_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=255)
    parent_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = None
    created_by: Optional[str] = Field(default=None, max_length=100)
    is_directory: bool = False
    ai_suggest: list[RequirementFinding] = Field(default_factory=list)


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    project_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    parent_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = None
    created_by: Optional[str] = Field(default=None, max_length=100)
    is_directory: Optional[bool] = None
    ai_suggest: Optional[list[RequirementFinding]] = None


class DocumentOut(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RequirementReviewRequest(BaseModel):
    document_id: Optional[int] = None
    title: Optional[str] = None
    content: str = Field(min_length=1)
    extra_prompt: Optional[str] = Field(default=None, max_length=1000)


class RequirementReviewResponse(BaseModel):
    document_id: Optional[int] = None
    title: Optional[str] = None
    findings: list[RequirementFinding]
