from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.persona import Persona
from security import get_current_user_id

router = APIRouter(prefix="/api/personas", tags=["人格管理"])


class PersonaCreate(BaseModel):
    name: str
    personality: str
    speaking_style: str
    background: str = ""


@router.get("")
async def list_personas(db: Session = Depends(get_db)):
    return [p.to_dict() for p in db.query(Persona).all()]


@router.post("")
async def create_persona(data: PersonaCreate, db: Session = Depends(get_db)):
    persona = Persona(**data.model_dump())
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona.to_dict()


@router.delete("/{persona_id}")
async def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = db.get(Persona, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="人格不存在")
    db.delete(persona)
    db.commit()
    return {"ok": True}
