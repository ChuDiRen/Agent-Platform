from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class ApiDocument(Base):
    __tablename__ = "api_documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, nullable=True, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    is_directory = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ai_suggest = Column(Text, nullable=True)
