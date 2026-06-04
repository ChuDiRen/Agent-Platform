import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.api_document import ApiDocument
from app.schemas.api_document import ApiDocumentCreate, ApiDocumentUpdate


class CRUDApiDocument(CRUDBase[ApiDocument, ApiDocumentCreate, ApiDocumentUpdate]):
    def get_multi_by_project(
        self, db: Session, *, project_id: int | None = None, skip: int = 0, limit: int = 200
    ) -> list[ApiDocument]:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        return query.order_by(self.model.parent_id.isnot(None), self.model.id).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ApiDocumentCreate) -> ApiDocument:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["ai_suggest"] = json.dumps(obj_in_data.get("ai_suggest") or [], ensure_ascii=False)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ApiDocument, obj_in: ApiDocumentUpdate) -> ApiDocument:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "ai_suggest" in update_data and update_data["ai_suggest"] is not None:
            update_data["ai_suggest"] = json.dumps(jsonable_encoder(update_data["ai_suggest"]), ensure_ascii=False)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


api_document = CRUDApiDocument(ApiDocument)
