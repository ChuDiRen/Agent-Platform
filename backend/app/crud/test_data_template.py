import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.test_data_template import TestDataTemplate
from app.schemas.test_data import TestDataTemplateCreate, TestDataTemplateUpdate


class CRUDTestDataTemplate(
    CRUDBase[TestDataTemplate, TestDataTemplateCreate, TestDataTemplateUpdate]
):
    def get_multi_by_project(
        self, db: Session, *, project_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[TestDataTemplate]:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: TestDataTemplateCreate) -> TestDataTemplate:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["fields"] = json.dumps(obj_in_data["fields"], ensure_ascii=False)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: TestDataTemplate, obj_in: TestDataTemplateUpdate
    ) -> TestDataTemplate:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "fields" in update_data and update_data["fields"] is not None:
            update_data["fields"] = json.dumps(
                jsonable_encoder(update_data["fields"]), ensure_ascii=False
            )
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


test_data_template = CRUDTestDataTemplate(TestDataTemplate)
