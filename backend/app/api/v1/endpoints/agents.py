from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_admin
from app.crud.agent import agent as agent_crud
from app.schemas.agent import AgentOut, AgentCreate, AgentUpdate
from app.core.response import success, fail

router = APIRouter()


@router.get("/")
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = (
        db.query(agent_crud.model)
        .order_by(agent_crud.model.sort_order.asc(), agent_crud.model.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return success(data=[AgentOut.model_validate(a).model_dump() for a in items])


@router.get("/{agent_id}")
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    ag = agent_crud.get(db, agent_id)
    if not ag:
        return fail(message="Agent not found", code=404)
    return success(data=AgentOut.model_validate(ag).model_dump())


@router.post("/", dependencies=[Depends(require_admin)])
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    obj = agent_crud.create(db, obj_in=agent_in)
    return success(data=AgentOut.model_validate(obj).model_dump())


@router.put("/{agent_id}", dependencies=[Depends(require_admin)])
def update_agent(agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    ag = agent_crud.get(db, agent_id)
    if not ag:
        return fail(message="Agent not found", code=404)
    updated = agent_crud.update(db, db_obj=ag, obj_in=agent_in)
    return success(data=AgentOut.model_validate(updated).model_dump())


@router.delete("/{agent_id}", dependencies=[Depends(require_admin)])
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    ag = agent_crud.get(db, agent_id)
    if not ag:
        return fail(message="Agent not found", code=404)
    removed = agent_crud.remove(db, id=agent_id)
    return success(data=AgentOut.model_validate(removed).model_dump())
