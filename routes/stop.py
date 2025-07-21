from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Stop, StopCause
from schemas import StopCreate, StopUpdate, StopOut
from auth import get_current_user

router = APIRouter(prefix="/stops", tags=["stops"])

@router.post("/", response_model=StopOut, status_code=status.HTTP_201_CREATED)
def create_stop(data: StopCreate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):

    stop_cause=db.query(StopCause).filter(StopCause.factory_id==current_user.factory_id,StopCause.id==data.stop_cause_id).first()
    if not stop_cause:
        raise HTTPException(status_code=404, detail="Stop Cause not found")
    
    stop = Stop(**data.dict())
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop

@router.get("/", response_model=List[StopOut])
def list_stops(db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(Stop).all()


@router.get("/machine/{machine_id}", response_model=List[StopOut])
def list_stops_by_machine(machine_id:int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(Stop).filter(Stop.machine_id==machine_id,Stop.end_datetime==None).all()


@router.get("/{stop_id}", response_model=StopOut)
def get_stop(stop_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    stop = db.query(Stop).join(StopCause,Stop.stop_cause_id==StopCause.id).filter(StopCause.factory_id==current_user.factory_id,Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop

@router.put("/{stop_id}", response_model=StopOut)
def update_stop(stop_id: int, data: StopUpdate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):

    stop_cause=db.query(StopCause).filter(StopCause.factory_id==current_user.factory_id,StopCause.id==data.stop_cause_id).first()
    if not stop_cause:
        raise HTTPException(status_code=404, detail="Stop Cause not found")
    
    stop = db.query(Stop).filter(StopCause.factory_id==current_user.factory_id,Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(stop, key, value)

    db.commit()
    db.refresh(stop)
    return stop

@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    stop = db.query(Stop).join(StopCause,Stop.stop_cause_id==StopCause.id).filter(StopCause.factory_id==current_user.factory_id,Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    db.delete(stop)
    db.commit()
