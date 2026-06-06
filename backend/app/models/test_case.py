from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    module_id = Column(Integer, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    priority = Column(Integer, default=2)
    precondition = Column(String(1024), nullable=True)
    expected = Column(String(1024), nullable=True)
    steps = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
