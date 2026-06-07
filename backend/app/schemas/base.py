"""
基础 Pydantic schemas

提供通用响应模型和分页/ID 等基础 schema。
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """通用 API 响应模型，配合 FastAPI 的 response_model 使用"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)


class PageRequest(BaseModel):
    """分页请求参数"""
    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页条数")

    model_config = ConfigDict(from_attributes=True)


class IDResponse(BaseModel):
    """仅含 ID 的响应，适用于创建/删除等返回主键的场景"""
    id: int = Field(description="记录 ID")

    model_config = ConfigDict(from_attributes=True)
