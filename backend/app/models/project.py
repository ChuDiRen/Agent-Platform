from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    password = Column(String(255))
    llm_url = Column(String(255))
    llm_key = Column(String(255))
    llm_model = Column(String(255))
    lvm_url = Column(String(255))
    lvm_key = Column(String(255))
    lvm_model = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    extend_json = Column(Text)
