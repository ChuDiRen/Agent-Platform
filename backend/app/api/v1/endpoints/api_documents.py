import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.api_document import api_document as api_document_crud
from app.schemas.api_document import (
    ApiDocumentAnalysisRequest,
    ApiDocumentAnalysisResponse,
    ApiDocumentCreate,
    ApiDocumentOut,
    ApiDocumentUpdate,
)
from app.services.api_document_analysis import analyze_api_document

router = APIRouter()


def _api_document_to_out(document) -> ApiDocumentOut:
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
    return ApiDocumentOut.model_validate(data)


@router.get("/", response_model=list[ApiDocumentOut])
def read_api_documents(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    documents = api_document_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return [_api_document_to_out(document) for document in documents]


@router.post("/", response_model=ApiDocumentOut)
def create_api_document(document_in: ApiDocumentCreate, db: Session = Depends(get_db)):
    document = api_document_crud.create(db, obj_in=document_in)
    return _api_document_to_out(document)


@router.get("/{document_id}", response_model=ApiDocumentOut)
def read_api_document(document_id: int, db: Session = Depends(get_db)):
    document = api_document_crud.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="API document not found")
    return _api_document_to_out(document)


@router.put("/{document_id}", response_model=ApiDocumentOut)
def update_api_document(
    document_id: int,
    document_in: ApiDocumentUpdate,
    db: Session = Depends(get_db),
):
    document = api_document_crud.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="API document not found")
    updated = api_document_crud.update(db, db_obj=document, obj_in=document_in)
    return _api_document_to_out(updated)


@router.delete("/{document_id}", response_model=ApiDocumentOut)
def delete_api_document(document_id: int, db: Session = Depends(get_db)):
    document = api_document_crud.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="API document not found")
    removed = api_document_crud.remove(db, id=document_id)
    return _api_document_to_out(removed)


@router.post("/analysis", response_model=ApiDocumentAnalysisResponse)
def analyze_document(payload: ApiDocumentAnalysisRequest):
    return analyze_api_document(payload)
