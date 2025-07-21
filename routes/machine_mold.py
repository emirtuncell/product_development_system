from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import MachineMold,Machine,Mold
from schemas import MachineMoldCreate, MachineMoldUpdate, MachineMoldOut
from auth import get_current_user

router = APIRouter(prefix="/machine-molds", tags=["machine_molds"])

@router.post("/", response_model=MachineMoldOut, status_code=status.HTTP_201_CREATED)
def create_machine_mold(data: MachineMoldCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    machine=db.query(Machine).filter(Machine.factory_id==current_user.factory_id,Machine.id==data.machine_id).first()
    mold=db.query(Mold).filter(Mold.factory_id==current_user.factory_id,Mold.id==data.mold_id).first()
    
    if not machine or not mold:
        raise HTTPException(status_code=400, detail="Machine or Mold not exists.")
    
    record=db.query(MachineMold).filter(MachineMold.machine_id==data.machine_id,MachineMold.mold_id==data.mold_id).first()

    if record:
        raise HTTPException(status_code=400, detail="Machine-Mold pair already exists.")
    
    machine_mold = MachineMold(**data.dict())
    db.add(machine_mold)
    db.commit()
    return machine_mold

@router.get("/", response_model=List[MachineMoldOut])
def list_machine_molds(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MachineMold).join(Machine,Machine.id==MachineMold.machine_id).join(Mold,Mold.id==MachineMold.mold_id).filter(Machine.factory_id==current_user.factory_id).filter(Mold.factory_id==current_user.factory_id).all()


@router.get("/machine/{machine_id}", response_model=List[MachineMoldOut])
def list_machine_molds_by_machine(machine_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MachineMold) \
        .join(Machine,Machine.id==MachineMold.machine_id)\
        .join(Mold,Mold.id==MachineMold.mold_id)\
        .filter(Machine.factory_id==current_user.factory_id)\
        .filter(
            Mold.factory_id==current_user.factory_id,
            MachineMold.machine_id==machine_id
            )\
        .all()

@router.get("/mold/{mold_id}", response_model=List[MachineMoldOut])
def list_machine_molds_by_mold(mold_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MachineMold) \
        .join(Machine,Machine.id==MachineMold.machine_id)\
        .join(Mold,Mold.id==MachineMold.mold_id)\
        .filter(Machine.factory_id==current_user.factory_id)\
        .filter(
            Mold.factory_id==current_user.factory_id,
            MachineMold.mold_id==mold_id
            )\
        .all()

@router.get("/{machine_mold_id}", response_model=MachineMoldOut)
def get_machine_mold(machine_mold_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(MachineMold).join(Machine,Machine.id==MachineMold.machine_id).join(Mold,Mold.id==MachineMold.mold_id).filter(Machine.factory_id==current_user.factory_id).filter(Mold.factory_id==current_user.factory_id).filter(MachineMold.id == machine_mold_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Machine-Mold not found")
    return record

@router.put("/{machine_mold_id}", response_model=MachineMoldOut)
def update_machine_mold(machine_mold_id: int, data: MachineMoldUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    machine=db.query(Machine).filter(Machine.factory_id==current_user.factory_id,Machine.id==data.machine_id).first()
    mold=db.query(Mold).filter(Mold.factory_id==current_user.factory_id,Mold.id==data.mold_id).first()
    if not machine or not mold:
        raise HTTPException(status_code=400, detail="Machine or Mold not exists.")
    
    record = db.query(MachineMold).filter(MachineMold.id == machine_mold_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Machine-Mold not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Machine-Mold pair already exists.")
    db.refresh(record)
    return record

@router.delete("/{machine_mold_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine_mold(machine_mold_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(MachineMold).join(Machine,Machine.id==MachineMold.machine_id).join(Mold,Mold.id==MachineMold.mold_id).filter(Machine.factory_id==current_user.factory_id).filter(Mold.factory_id==current_user.factory_id).filter(MachineMold.id == machine_mold_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Machine-Mold not found")
    db.delete(record)
    db.commit()
