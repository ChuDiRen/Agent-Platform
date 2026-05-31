import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.document import document as document_crud
from app.schemas.document import (
    DocumentCreate,
    DocumentOut,
    DocumentUpdate,
    RequirementReviewRequest,
    RequirementReviewResponse,
)
from app.services.requirement_review import review_requirement

router = APIRouter()


def _document_to_out(document) -> DocumentOut:
    data = {
        "id": document.id,
        "project_id": document.project_id,
        "name": document.name,
        "parent_id": document.parent_id,
        "title": document.title,
        "content": document.content,
        "created_by": document.created_by,
        "is_directory": document.is_directory,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "ai_suggest": json.loads(document.ai_suggest or "[]"),
    }
    return DocumentOut.model_validate(data)


@router.get("/", response_model=list[DocumentOut])
def read_documents(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    documents = document_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return [_document_to_out(document) for document in documents]


@router.post("/", response_model=DocumentOut)
def create_document(document_in: DocumentCreate, db: Session = Depends(get_db)):
    document = document_crud.create(db, obj_in=document_in)
    return _document_to_out(document)


@router.get("/{document_id}", response_model=DocumentOut)
def read_document(document_id: int, db: Session = Depends(get_db)):
    document = document_crud.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return _document_to_out(document)


@router.put("/{document_id}", response_model=DocumentOut)
def update_document(
    document_id: int,
    document_in: DocumentUpdate,
    db: Session = Depends(get_db),
):
    document = document_crud.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    updated = document_crud.update(db, db_obj=document, obj_in=document_in)
    return _document_to_out(updated)


@router.delete("/{document_id}", response_model=DocumentOut)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = document_crud.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    removed = document_crud.remove(db, id=document_id)
    return _document_to_out(removed)


@router.post("/review", response_model=RequirementReviewResponse)
def review_document(payload: RequirementReviewRequest):
    return review_requirement(payload)
