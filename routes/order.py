from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import Order, Customer
from schemas import OrderCreate, OrderUpdate, OrderOut
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.factory_id == current_user.factory_id, Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found.")

    record = Order(**data.dict())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred.")
    
    return record


@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Order).join(Customer,Customer.id==Order.customer_id).filter(Customer.factory_id == current_user.factory_id).all()


@router.get("/customer/{customer_id}", response_model=List[OrderOut])
def list_customer_orders(customer_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Order).join(Customer,Customer.id==Order.customer_id).filter(Order.customer_id==customer_id,Customer.factory_id == current_user.factory_id).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(Order).join(Customer,Customer.id==Order.customer_id).filter(Customer.factory_id == current_user.factory_id, Order.id == order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Order not found")
    return record


@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(Order).join(Customer,Customer.id==Order.customer_id).filter(Customer.factory_id == current_user.factory_id, Order.id == order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Order not found")

    # Müşteri doğrulaması gerekiyorsa:
    if data.customer_id is not None:
        customer = db.query(Customer).filter(Customer.factory_id == current_user.factory_id, Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(Order).join(Customer,Customer.id==Order.customer_id).filter(Customer.factory_id == current_user.factory_id, Order.id == order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(record)
    db.commit()
