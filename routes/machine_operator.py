from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import MachineOperator,Machine,Operator
from schemas import MachineOperatorCreate, MachineOperatorUpdate, MachineOperatorOut
from auth import get_current_user

router = APIRouter(prefix="/machine-operators", tags=["machine_operators"])

@router.post("/", response_model=MachineOperatorOut, status_code=status.HTTP_201_CREATED)
def create_machine_operator(data: MachineOperatorCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    machine=db.query(Machine).filter(Machine.factory_id==current_user.factory_id,Machine.id==data.machine_id).first()
    operator=db.query(Operator).filter(Operator.factory_id==current_user.factory_id,Operator.id==data.operator_id).first()
    
    if not machine or not operator:
        raise HTTPException(status_code=400, detail="Machine or Operator not exists.")
    
    record=db.query(MachineOperator).filter(MachineOperator.machine_id==data.machine_id,MachineOperator.operator_id==data.operator_id).first()

    if record:
        raise HTTPException(status_code=400, detail="Machine-Operator pair already exists.")
    
    record = MachineOperator(**data.dict())
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Machine-Operator pair already exists.")
    db.refresh(record)
    return record

@router.get("/", response_model=List[MachineOperatorOut])
def list_machine_operators(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MachineOperator).join(Machine,Machine.id==MachineOperator.machine_id).join(Operator,Operator.id==MachineOperator.operator_id).filter(Machine.factory_id==current_user.factory_id).filter(Operator.factory_id==current_user.factory_id,Operator.is_deleted!=True).all()

@router.get("/machine/{machine_id}", response_model=List[MachineOperatorOut])
def list_machine_operators_by_machine(machine_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MachineOperator).join(Machine,Machine.id==MachineOperator.machine_id).join(Operator,Operator.id==MachineOperator.operator_id).filter(Machine.factory_id==current_user.factory_id).filter(Operator.factory_id==current_user.factory_id,MachineOperator.machine_id==machine_id,Operator.is_deleted!=True).all()

@router.get("/operator/{operator_id}", response_model=List[MachineOperatorOut])
def list_machine_operators_by_operator(operator_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MachineOperator).join(Machine,Machine.id==MachineOperator.machine_id).join(Operator,Operator.id==MachineOperator.operator_id).filter(Machine.factory_id==current_user.factory_id).filter(Operator.factory_id==current_user.factory_id,MachineOperator.operator_id==operator_id).all()


@router.get("/{machine_operator_id}", response_model=MachineOperatorOut)
def get_machine_operator(machine_operator_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(MachineOperator).join(Machine,Machine.id==MachineOperator.machine_id).join(Operator,Operator.id==MachineOperator.operator_id).filter(Machine.factory_id==current_user.factory_id).filter(Operator.factory_id==current_user.factory_id).filter(MachineOperator.id == machine_operator_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Machine-Operator not found")
    return record

@router.put("/{machine_operator_id}", response_model=MachineOperatorOut)
def update_machine_operator(machine_operator_id: int, data: MachineOperatorUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    machine=db.query(Machine).filter(Machine.factory_id==current_user.factory_id,Machine.id==data.machine_id).first()
    operator=db.query(Operator).filter(Operator.factory_id==current_user.factory_id,Operator.id==data.operator_id).first()
    
    if not machine or not operator:
        raise HTTPException(status_code=400, detail="Machine or Operator not exists.")

    record = db.query(MachineOperator).filter(MachineOperator.id == machine_operator_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Machine-Operator not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Machine-Operator pair already exists.")
    db.refresh(record)
    return record

@router.delete("/{machine_operator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine_operator(machine_operator_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(MachineOperator).join(Machine,Machine.id==MachineOperator.machine_id).join(Operator,Operator.id==MachineOperator.operator_id).filter(Machine.factory_id==current_user.factory_id).filter(Operator.factory_id==current_user.factory_id).filter(MachineOperator.id == machine_operator_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Machine-Operator not found")
    db.delete(record)
    db.commit()
