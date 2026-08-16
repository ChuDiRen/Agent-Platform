from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    # 项目访问密码：仅存 bcrypt 哈希，绝不存明文、绝不回传
    password_hash = Column(String(255))
    # 数据归属：创建者；admin 可管理所有项目
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    llm_url = Column(String(255))
    llm_model = Column(String(255))
    lvm_url = Column(String(255))
    lvm_model = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    extend_json = Column(Text)

    @property
    def has_password(self) -> bool:
        return bool(self.password_hash)
