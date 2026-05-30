from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    password: Optional[str] = None
    llm_url: Optional[str] = None
    llm_key: Optional[str] = None
    llm_model: Optional[str] = None
    lvm_url: Optional[str] = None
    lvm_key: Optional[str] = None
    lvm_model: Optional[str] = None
    extend_json: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    password: Optional[str] = None
    llm_url: Optional[str] = None
    llm_key: Optional[str] = None
    llm_model: Optional[str] = None
    lvm_url: Optional[str] = None
    lvm_key: Optional[str] = None
    lvm_model: Optional[str] = None
    extend_json: Optional[str] = None


class Project(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
