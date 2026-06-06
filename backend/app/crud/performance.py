import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.performance import Performance
from app.schemas.performance import PerformanceCreate, PerformanceUpdate


class CRUDPerformance(CRUDBase[Performance, PerformanceCreate, PerformanceUpdate]):
    def get_multi_by_project(
        self, db: Session, *, project_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[Performance]:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: PerformanceCreate) -> Performance:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["configs"] = json.dumps(obj_in_data["configs"], ensure_ascii=False)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Performance, obj_in: PerformanceUpdate) -> Performance:
        update_data = jsonable_encoder(obj_in.model_dump(exclude_unset=True))
        if "configs" in update_data and update_data["configs"] is not None:
            update_data["configs"] = json.dumps(update_data["configs"], ensure_ascii=False)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


performance = CRUDPerformance(Performance)
