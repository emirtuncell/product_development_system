from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import StopCause
from database import get_db
from schemas import StopCauseCreate, StopCauseUpdate, StopCauseOut
from auth import get_current_user

router = APIRouter(prefix="/stop-causes", tags=["stop_causes"])

@router.post("/", response_model=StopCauseOut, status_code=status.HTTP_201_CREATED)
def create_stop_cause(data: StopCauseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        stop_cause = StopCause(**data.dict(),factory_id=current_user.factory_id)
        db.add(stop_cause)
        db.commit()
        db.refresh(stop_cause)
        return stop_cause
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=List[StopCauseOut])
def list_stop_causes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(StopCause).filter(StopCause.factory_id==current_user.factory_id).all()

@router.get("/{stop_cause_id}", response_model=StopCauseOut)
def get_stop_cause(stop_cause_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    stop_cause = db.query(StopCause).filter(StopCause.id == stop_cause_id,StopCause.factory_id==current_user.factory_id).first()
    if not stop_cause:
        raise HTTPException(status_code=404, detail="Stop cause not found")
    return stop_cause

@router.put("/{stop_cause_id}", response_model=StopCauseOut)
def update_stop_cause(stop_cause_id: int, update_data: StopCauseUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        stop_cause = db.query(StopCause).filter(StopCause.id == stop_cause_id,StopCause.factory_id==current_user.factory_id).first()
        if not stop_cause:
            raise HTTPException(status_code=404, detail="Stop cause not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(stop_cause, key, value)
        db.commit()
        db.refresh(stop_cause)
        return stop_cause
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{stop_cause_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop_cause(stop_cause_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    stop_cause = db.query(StopCause).filter(StopCause.id == stop_cause_id,StopCause.factory_id==current_user.factory_id).first()
    if not stop_cause:
        raise HTTPException(status_code=404, detail="Stop cause not found")
    db.delete(stop_cause)
    db.commit()
