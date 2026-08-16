import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.api_automation_case import ApiAutomationCase
from app.schemas.api_automation import ApiAutomationCaseCreate, ApiAutomationCaseUpdate


class CRUDApiAutomationCase(
    CRUDBase[ApiAutomationCase, ApiAutomationCaseCreate, ApiAutomationCaseUpdate]
):
    def get_multi_filtered(
        self,
        db: Session,
        *,
        project_id: int | None = None,
        name: str | None = None,
        priority: int | None = None,
        module_id: int | None = None,
        exec_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ApiAutomationCase]:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        if name:
            query = query.filter(self.model.name.contains(name))
        if priority is not None:
            query = query.filter(self.model.priority == priority)
        if module_id is not None:
            query = query.filter(self.model.module_id == module_id)
        if exec_type:
            query = query.filter(self.model.exec_type == exec_type)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def count_filtered(
        self,
        db: Session,
        *,
        project_id: int | None = None,
        name: str | None = None,
        priority: int | None = None,
        module_id: int | None = None,
        exec_type: str | None = None,
    ) -> int:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        if name:
            query = query.filter(self.model.name.contains(name))
        if priority is not None:
            query = query.filter(self.model.priority == priority)
        if module_id is not None:
            query = query.filter(self.model.module_id == module_id)
        if exec_type:
            query = query.filter(self.model.exec_type == exec_type)
        return query.count()

    def create(self, db: Session, *, obj_in: ApiAutomationCaseCreate) -> ApiAutomationCase:
        data = jsonable_encoder(obj_in)
        data["request"] = json.dumps(data.get("request") or {}, ensure_ascii=False)
        db_obj = self.model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ApiAutomationCase, obj_in: ApiAutomationCaseUpdate
    ) -> ApiAutomationCase:
        data = jsonable_encoder(obj_in.model_dump(exclude_unset=True))
        if "request" in data and data["request"] is not None:
            data["request"] = json.dumps(data["request"], ensure_ascii=False)
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


api_automation_case = CRUDApiAutomationCase(ApiAutomationCase)
