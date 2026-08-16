from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    password: Optional[str] = None
    llm_url: Optional[str] = None
    llm_model: Optional[str] = None
    lvm_url: Optional[str] = None
    lvm_model: Optional[str] = None
    extend_json: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    password: Optional[str] = None
    llm_url: Optional[str] = None
    llm_model: Optional[str] = None
    lvm_url: Optional[str] = None
    lvm_model: Optional[str] = None
    extend_json: Optional[str] = None


class ProjectOut(BaseModel):
    """项目输出模型：绝不包含密码或密钥明文。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    has_password: bool = False
    llm_url: Optional[str] = None
    llm_model: Optional[str] = None
    lvm_url: Optional[str] = None
    lvm_model: Optional[str] = None
    extend_json: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectVerifyRequest(BaseModel):
    """项目密码校验请求。"""

    password: str = Field(min_length=1)


class ProjectVerifyResponse(BaseModel):
    valid: bool
