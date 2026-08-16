from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class ApiAutomationCase(Base):
    """接口自动化用例（真实数据源，替代原 stub）。"""

    __tablename__ = "api_automation_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    module_id = Column(Integer, nullable=True, index=True)
    module_name = Column(String(255), nullable=False, default="")
    exec_type = Column(String(255), nullable=False, default="HTTP 请求")
    priority = Column(Integer, nullable=False, default=2)
    name = Column(String(255), nullable=False)
    # request 定义（JSON: method/path/url_params/form/json/headers/cookies）
    request = Column(Text, nullable=False, default="{}")
    expected = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
