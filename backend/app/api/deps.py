from typing import Any, Generic, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud.base import CRUDBase
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        crud: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
        prefix: str = "",
        tag: str = "",
    ):
        self.crud = crud
        self.router = APIRouter(prefix=prefix, tags=[tag] if tag else [])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/", response_model=Any)
        def create_item(obj_in: CreateSchemaType, db: Session = Depends(get_db)):
            return self.crud.create(db, obj_in=obj_in)

        @self.router.get("/{item_id}", response_model=Any)
        def read_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.get("/", response_model=list[Any])
        def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return self.crud.get_multi(db, skip=skip, limit=limit)

        @self.router.put("/{item_id}", response_model=Any)
        def update_item(
            item_id: int, obj_in: UpdateSchemaType, db: Session = Depends(get_db)
        ):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.update(db, db_obj=item, obj_in=obj_in)

        @self.router.delete("/{item_id}", response_model=Any)
        def delete_item(item_id: int, db: Session = Depends(get_db)):
            item = self.crud.get(db, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return self.crud.remove(db, id=item_id)
