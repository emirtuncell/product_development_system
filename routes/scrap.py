from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Scrap, ScrapCause
from schemas import ScrapCreate, ScrapUpdate, ScrapOut
from auth import get_current_user

router = APIRouter(prefix="/scraps", tags=["scraps"])

@router.post("/", response_model=ScrapOut, status_code=status.HTTP_201_CREATED)
def create_scrap(data: ScrapCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    scrap_cause=db.query(ScrapCause).filter(ScrapCause.factory_id==current_user.factory_id,ScrapCause.id==data.scrap_cause_id).first()
    if not scrap_cause:
        raise HTTPException(status_code=404, detail="Scrap Cause not found")
    scrap = Scrap(**data.dict())
    db.add(scrap)
    db.commit()
    db.refresh(scrap)
    return scrap

@router.get("/", response_model=List[ScrapOut])
def list_scraps(db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(Scrap).join(ScrapCause, Scrap.scrap_cause_id==ScrapCause.id).filter(ScrapCause.factory_id==current_user.factory_id).all()

@router.get("/{scrap_id}", response_model=ScrapOut)
def get_scrap(scrap_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    scrap = db.query(Scrap).join(ScrapCause, Scrap.scrap_cause_id==ScrapCause.id).filter(Scrap.id == scrap_id,ScrapCause.factory_id==current_user.factory_id).first()
    if not scrap:
        raise HTTPException(status_code=404, detail="Scrap not found")
    return scrap

@router.put("/{scrap_id}", response_model=ScrapOut)
def update_scrap(scrap_id: int, data: ScrapUpdate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):

    scrap_cause=db.query(ScrapCause).filter(ScrapCause.factory_id==current_user.factory_id,ScrapCause.id==data.scrap_cause_id).first()
    if not scrap_cause:
        raise HTTPException(status_code=404, detail="Scrap Cause not found")
 
    scrap = db.query(Scrap).join(ScrapCause, Scrap.scrap_cause_id==ScrapCause.id).filter(Scrap.id == scrap_id,ScrapCause.factory_id==current_user.factory_id).first()
    if not scrap:
        raise HTTPException(status_code=404, detail="Scrap not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(scrap, key, value)

    db.commit()
    db.refresh(scrap)
    return scrap

@router.delete("/{scrap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scrap(scrap_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    scrap = db.query(Scrap).join(ScrapCause, Scrap.scrap_cause_id==ScrapCause.id).filter(Scrap.id == scrap_id,ScrapCause.factory_id==current_user.factory_id).first()
    if not scrap:
        raise HTTPException(status_code=404, detail="Scrap not found")
    db.delete(scrap)
    db.commit()
