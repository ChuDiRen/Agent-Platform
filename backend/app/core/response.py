"""
统一 API 响应模型和工具函数

响应格式:
  成功: {"code": 0, "message": "success", "data": T}
  失败: {"code": 非零, "message": "错误信息", "data": null}
  分页: {"code": 0, "message": "success", "data": {"items": [], "total": N, "page": P, "page_size": S}}
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


# ---------- Pydantic 模型 ----------

class BaseResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PaginationData(BaseModel, Generic[T]):
    """分页数据"""
    items: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[PaginationData[T]] = None


# ---------- 工具函数 (直接返回 dict，用于端点) ----------

def success(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def fail(message: str = "error", code: int = -1, data: Any = None) -> Dict[str, Any]:
    """失败响应"""
    return {"code": code, "message": message, "data": data}


def paginated(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = "success",
) -> Dict[str, Any]:
    """分页响应"""
    return {
        "code": 0,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }
