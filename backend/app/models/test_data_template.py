from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.db.base_class import Base


class TestDataTemplate(Base):
    __tablename__ = "test_data_templates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    fields = Column(Text, nullable=False)
    hint = Column(String(1000))
    count = Column(Integer, default=10)
    format = Column(String(45), default="json")
    lang = Column(String(45), default="zh")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
