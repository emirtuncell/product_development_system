from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Operator
from database import get_db
from schemas import OperatorCreate, OperatorUpdate, OperatorOut
from auth import get_current_user

router = APIRouter(prefix="/operators", tags=["operators"])

@router.post("/", response_model=OperatorOut, status_code=status.HTTP_201_CREATED)
def create_operator(operator: OperatorCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_operator = Operator(**operator.dict(),factory_id=current_user.factory_id)
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

@router.get("/", response_model=List[OperatorOut])
def list_operators(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Operator).filter(Operator.is_deleted == False,Operator.factory_id==current_user.factory_id).all()

@router.get("/{operator_id}", response_model=OperatorOut)
def get_operator(operator_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    operator = db.query(Operator).filter(Operator.id == operator_id, Operator.is_deleted == False,Operator.factory_id==current_user.factory_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    return operator

@router.put("/{operator_id}", response_model=OperatorOut)
def update_operator(operator_id: int, update_data: OperatorUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    operator = db.query(Operator).filter(Operator.id == operator_id,Operator.factory_id==current_user.factory_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(operator, key, value)
    db.commit()
    db.refresh(operator)
    return operator

@router.delete("/{operator_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_operator(operator_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    operator = db.query(Operator).filter(Operator.id == operator_id,Operator.factory_id==current_user.factory_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    operator.is_deleted = True
    db.commit()
