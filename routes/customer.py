from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Customer
from database import get_db
from schemas import CustomerCreate, CustomerUpdate, CustomerOut
from auth import get_current_user

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_customer = Customer(**customer.dict(), factory_id=current_user.factory_id)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerOut])
def list_customers(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Customer).filter(Customer.is_deleted == False, Customer.factory_id==current_user.factory_id).all()

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False, Customer.factory_id==current_user.factory_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, update_data: CustomerUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.id == customer_id,Customer.factory_id==current_user.factory_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_customer(customer_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.id == customer_id,Customer.factory_id==current_user.factory_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.is_deleted = True
    db.commit()
