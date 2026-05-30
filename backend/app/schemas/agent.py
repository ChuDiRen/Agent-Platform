from pydantic import BaseModel, ConfigDict
from typing import Optional


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[str] = None
    icon: Optional[str] = None
    gradient: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    is_placeholder: bool = False


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    icon: Optional[str] = None
    gradient: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_placeholder: Optional[bool] = None


class AgentOut(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
