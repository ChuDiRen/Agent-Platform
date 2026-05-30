from sqlalchemy import Column, Integer, String, Text, Boolean
from app.db.base_class import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(Text)          # JSON array string: '["tag1","tag2"]'
    icon = Column(String(50))
    gradient = Column(String(255))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_placeholder = Column(Boolean, default=False)
