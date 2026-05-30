from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.agent import agent as agent_crud
from app.schemas.agent import AgentOut, AgentCreate, AgentUpdate

router = APIRouter()


@router.get("/", response_model=list[AgentOut])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return agent_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=AgentOut)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    ag = agent_crud.get(db, agent_id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ag


@router.post("/", response_model=AgentOut)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    return agent_crud.create(db, obj_in=agent_in)


@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    ag = agent_crud.get(db, agent_id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_crud.update(db, db_obj=ag, obj_in=agent_in)


@router.delete("/{agent_id}", response_model=AgentOut)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    ag = agent_crud.get(db, agent_id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_crud.remove(db, id=agent_id)
