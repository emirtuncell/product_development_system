from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from sqlalchemy import or_

from database import get_db
from models import OrderProduct, Order, Product, Customer
from schemas import OrderProductCreate, OrderProductUpdate, OrderProductOut
from auth import get_current_user

router = APIRouter(prefix="/order-products", tags=["order_products"])


@router.post("/", response_model=OrderProductOut, status_code=status.HTTP_201_CREATED)
def create_order_product(data: OrderProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).join(Customer, Order.customer_id==Customer.id).filter(Customer.factory_id == current_user.factory_id, Order.id == data.order_id).first()
    product = db.query(Product).filter(Product.factory_id == current_user.factory_id, Product.id == data.product_id).first()

    if not order or not product:
        raise HTTPException(status_code=400, detail="Order or Product not found.")

    existing = db.query(OrderProduct).filter(
        OrderProduct.order_id == data.order_id,
        OrderProduct.product_id == data.product_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Order-Product pair already exists.")

    record = OrderProduct(**data.dict())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred.")

    return record


@router.get("/", response_model=List[OrderProductOut])
def list_order_products(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(OrderProduct) \
        .join(Order, Order.id == OrderProduct.order_id) \
        .join(Product, Product.id == OrderProduct.product_id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(Customer.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id) \
        .all()


@router.get("/order/{order_id}", response_model=List[OrderProductOut])
def list_order_products_by_order(order_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(OrderProduct) \
        .join(Order, Order.id == OrderProduct.order_id) \
        .join(Product, Product.id == OrderProduct.product_id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            Product.factory_id == current_user.factory_id,
            Order.id==order_id
            ) \
        .all()


@router.get("/{order_product_id}", response_model=OrderProductOut)
def get_order_product(order_product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(OrderProduct) \
        .join(Order, Order.id == OrderProduct.order_id) \
        .join(Product, Product.id == OrderProduct.product_id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(Customer.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id) \
        .filter(OrderProduct.id == order_product_id) \
        .first()

    if not record:
        raise HTTPException(status_code=404, detail="Order-Product not found")

    return record


@router.put("/{order_product_id}", response_model=OrderProductOut)
def update_order_product(order_product_id: int, data: OrderProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    if data.order_id:
        order = db.query(Order).join(Customer, Order.customer_id==Customer.id).filter(Customer.factory_id == current_user.factory_id, Order.id == data.order_id).first()
        if not order:
            raise HTTPException(status_code=400, detail="Order not found.")
    if  data.product_id:
        product = db.query(Product).filter(Product.factory_id == current_user.factory_id, Product.id == data.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail="Product not found.")


    record = db.query(OrderProduct).filter(OrderProduct.id == order_product_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Order-Product not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Order-Product pair already exists.")

    return record


@router.delete("/{order_product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_product(order_product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(OrderProduct) \
        .join(Order, Order.id == OrderProduct.order_id) \
        .join(Product, Product.id == OrderProduct.product_id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(Customer.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id) \
        .filter(OrderProduct.id == order_product_id) \
        .first()

    if not record:
        raise HTTPException(status_code=404, detail="Order-Product not found")

    db.delete(record)
    db.commit()
