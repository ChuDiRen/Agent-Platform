import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
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
from app.core.response import success, fail, paginated
from app.schemas.agent_task import AgentTaskOut
from app.services.agent_task_enqueue import create_and_enqueue_agent_task
from app.utils.file_parser import extract_text, SUPPORTED_EXTENSIONS

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


@router.get("/")
def read_documents(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    documents = document_crud.get_multi_by_project(db, project_id=project_id, skip=skip, limit=limit)
    items = [_document_to_out(d).model_dump() for d in documents]
    page = skip // limit + 1 if limit > 0 else 1
    return paginated(items=items, total=len(items), page=page, page_size=limit)


@router.post("/")
def create_document(document_in: DocumentCreate, db: Session = Depends(get_db)):
    document = document_crud.create(db, obj_in=document_in)
    return success(data=_document_to_out(document).model_dump())


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: int = Form(1),
    parent_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    """上传文件并解析为文档内容。

    支持格式: .txt, .md, .json, .xml, .csv, .html, .doc, .docx, .pdf
    """
    raw = await file.read()
    if not raw:
        return fail(message="文件内容为空", code=400)

    try:
        content = extract_text(file.filename or "unknown.txt", raw)
    except ValueError as exc:
        return fail(message=str(exc), code=400)

    name = file.filename.rsplit(".", 1)[0] if file.filename and "." in file.filename else (file.filename or "未命名文档")

    doc_in = DocumentCreate(
        project_id=project_id,
        parent_id=parent_id,
        name=name,
        title=name,
        content=content,
        is_directory=False,
    )
    document = document_crud.create(db, obj_in=doc_in)
    return success(data=_document_to_out(document).model_dump())


@router.get("/{document_id}")
def read_document(document_id: int, db: Session = Depends(get_db)):
    document = document_crud.get(db, document_id)
    if not document:
        return fail(message="Document not found", code=404)
    return success(data=_document_to_out(document).model_dump())


@router.put("/{document_id}")
def update_document(
    document_id: int,
    document_in: DocumentUpdate,
    db: Session = Depends(get_db),
):
    document = document_crud.get(db, document_id)
    if not document:
        return fail(message="Document not found", code=404)
    updated = document_crud.update(db, db_obj=document, obj_in=document_in)
    return success(data=_document_to_out(updated).model_dump())


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = document_crud.get(db, document_id)
    if not document:
        return fail(message="Document not found", code=404)
    removed = document_crud.remove(db, id=document_id)
    return success(data=_document_to_out(removed).model_dump())


# ---------------------------------------------------------------------------
# AI 需求评估端点 (Deep Agents SDK)
# ---------------------------------------------------------------------------

@router.post("/review")
def review_document(payload: RequirementReviewRequest, db: Session = Depends(get_db)):
    """创建分布式需求评审任务。"""
    task = create_and_enqueue_agent_task(
        db,
        agent_key="requirement_review",
        input_payload=payload.model_dump(),
    )
    return success(data=AgentTaskOut.model_validate(task).model_dump(mode="json"))
