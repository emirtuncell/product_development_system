from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import ScrapCause
from database import get_db
from schemas import ScrapCauseCreate, ScrapCauseUpdate, ScrapCauseOut
from auth import get_current_user

router = APIRouter(prefix="/scrap-causes", tags=["scrap_causes"])

@router.post("/", response_model=ScrapCauseOut, status_code=status.HTTP_201_CREATED)
def create_scrap_cause(data: ScrapCauseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        scrap_cause = ScrapCause(**data.dict(), factory_id=current_user.factory_id)
        db.add(scrap_cause)
        db.commit()
        db.refresh(scrap_cause)
        return scrap_cause
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/", response_model=List[ScrapCauseOut])
def list_scrap_causes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(ScrapCause).filter(ScrapCause.factory_id==current_user.factory_id).all()

@router.get("/{scrap_cause_id}", response_model=ScrapCauseOut)
def get_scrap_cause(scrap_cause_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    scrap_cause = db.query(ScrapCause).filter(ScrapCause.id == scrap_cause_id,ScrapCause.factory_id==current_user.factory_id).first()
    if not scrap_cause:
        raise HTTPException(status_code=404, detail="Scrap cause not found")
    return scrap_cause

@router.put("/{scrap_cause_id}", response_model=ScrapCauseOut)
def update_scrap_cause(scrap_cause_id: int, update_data: ScrapCauseUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        scrap_cause = db.query(ScrapCause).filter(ScrapCause.id == scrap_cause_id,ScrapCause.factory_id==current_user.factory_id).first()
        if not scrap_cause:
            raise HTTPException(status_code=404, detail="Scrap cause not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(scrap_cause, key, value)
        db.commit()
        db.refresh(scrap_cause)
        return scrap_cause
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{scrap_cause_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scrap_cause(scrap_cause_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    scrap_cause = db.query(ScrapCause).filter(ScrapCause.id == scrap_cause_id,ScrapCause.factory_id==current_user.factory_id).first()
    if not scrap_cause:
        raise HTTPException(status_code=404, detail="Scrap cause not found")
    db.delete(scrap_cause)
    db.commit()
