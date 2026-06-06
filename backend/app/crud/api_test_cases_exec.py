import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.api_test_cases_exec import ApiTestCasesExec
from app.schemas.api_automation import ApiTestExecCreate, ApiTestExecUpdate


class CRUDApiTestCasesExec(CRUDBase[ApiTestCasesExec, ApiTestExecCreate, ApiTestExecUpdate]):
    def get_multi_by_project(
        self,
        db: Session,
        *,
        project_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ApiTestCasesExec]:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ApiTestExecCreate) -> ApiTestCasesExec:
        obj_in_data = jsonable_encoder(obj_in)
        for field in ("case_ids", "details", "exec_param"):
            obj_in_data[field] = json.dumps(obj_in_data.get(field) or ([] if field == "case_ids" else {}), ensure_ascii=False)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ApiTestCasesExec, obj_in: ApiTestExecUpdate) -> ApiTestCasesExec:
        update_data = jsonable_encoder(obj_in.model_dump(exclude_unset=True))
        for field in ("details", "exec_param"):
            if field in update_data and update_data[field] is not None:
                update_data[field] = json.dumps(update_data[field], ensure_ascii=False)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


api_test_cases_exec = CRUDApiTestCasesExec(ApiTestCasesExec)
