from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def create(self, db: Session, *, obj_in: ProjectCreate) -> Project:
        data = obj_in.model_dump(exclude_unset=True)
        password = data.pop("password", None) or None
        db_obj = Project(**data)
        if password:
            db_obj.password_hash = get_password_hash(password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Project, obj_in: ProjectUpdate) -> Project:
        data = obj_in.model_dump(exclude_unset=True)
        password = data.pop("password", None)
        for field, value in data.items():
            setattr(db_obj, field, value)
        if password is not None:
            # 传入空字符串表示清除密码，非空则哈希后更新
            db_obj.password_hash = get_password_hash(password) if password else None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def verify_password(self, db: Session, *, project: Project, password: str) -> bool:
        if not project.password_hash:
            return True  # 未设置密码的项目无需校验
        return verify_password(password, project.password_hash)


project = CRUDProject(Project)
