from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    project_id = Column(Integer, nullable=True, index=True)
    configs = Column(Text, nullable=True)
