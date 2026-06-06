from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class ApiTestCasesExec(Base):
    __tablename__ = "api_test_cases_exec"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    exec_type = Column(String(255), nullable=False, default="HTTP 请求")
    case_ids = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    desc = Column(String(1024), nullable=True)
    exec_param = Column(Text, nullable=True)
    exec_status = Column(String(255), nullable=False, default="已完成")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
