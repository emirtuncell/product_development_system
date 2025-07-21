from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Machine
from database import get_db
from schemas import MachineCreate, MachineUpdate, MachineOut
from auth import get_current_user

router = APIRouter(prefix="/machines", tags=["machines"])

@router.post("/", response_model=MachineOut, status_code=status.HTTP_201_CREATED)
def create_machine(machine: MachineCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        db_machine = Machine(**machine.dict(),factory_id=current_user.factory_id)
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        return db_machine
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[MachineOut])
def list_machines(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Machine).filter(Machine.is_deleted == False,Machine.factory_id==current_user.factory_id).all()

@router.get("/{machine_id}", response_model=MachineOut)
def get_machine(machine_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id, Machine.is_deleted == False,Machine.factory_id==current_user.factory_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.put("/{machine_id}", response_model=MachineOut)
def update_machine(machine_id: int, update_data: MachineUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        machine = db.query(Machine).filter(Machine.id == machine_id,Machine.factory_id==current_user.factory_id).first()
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(machine, key, value)
        db.commit()
        db.refresh(machine)
        return machine
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_machine(machine_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id,Machine.factory_id==current_user.factory_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    machine.is_deleted = True
    db.commit()
