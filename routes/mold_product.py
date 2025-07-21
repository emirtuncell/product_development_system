from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import MoldProduct, Mold, Product
from schemas import MoldProductCreate, MoldProductUpdate, MoldProductOut
from auth import get_current_user

router = APIRouter(prefix="/mold-products", tags=["mold_products"])


@router.post("/", response_model=MoldProductOut, status_code=status.HTTP_201_CREATED)
def create_mold_product(data: MoldProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mold = db.query(Mold).filter(Mold.factory_id == current_user.factory_id, Mold.id == data.mold_id).first()
    product = db.query(Product).filter(Product.factory_id == current_user.factory_id, Product.id == data.product_id).first()

    if not mold or not product:
        raise HTTPException(status_code=400, detail="Mold or Product not found.")

    existing = db.query(MoldProduct).filter(
        MoldProduct.mold_id == data.mold_id,
        MoldProduct.product_id == data.product_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Mold-Product pair already exists.")

    record = MoldProduct(**data.dict())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred.")
    
    return record


@router.get("/", response_model=List[MoldProductOut])
def list_mold_products(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MoldProduct) \
        .join(Mold, Mold.id == MoldProduct.mold_id) \
        .join(Product, Product.id == MoldProduct.product_id) \
        .filter(Mold.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id) \
        .all()


@router.get("/mold/{mold_id}", response_model=List[MoldProductOut])
def list_mold_products_by_mold(mold_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MoldProduct) \
        .join(Mold, Mold.id == MoldProduct.mold_id) \
        .join(Product, Product.id == MoldProduct.product_id) \
        .filter(Mold.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id,MoldProduct.mold_id==mold_id) \
        .all()


@router.get("/product/{product_id}", response_model=List[MoldProductOut])
def list_mold_products_by_product(product_id:int,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(MoldProduct) \
        .join(Mold, Mold.id == MoldProduct.mold_id) \
        .join(Product, Product.id == MoldProduct.product_id) \
        .filter(Mold.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id,MoldProduct.product_id==product_id) \
        .all()

@router.get("/{mold_product_id}", response_model=MoldProductOut)
def get_mold_product(mold_product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(MoldProduct) \
        .join(Mold, Mold.id == MoldProduct.mold_id) \
        .join(Product, Product.id == MoldProduct.product_id) \
        .filter(Mold.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id) \
        .filter(MoldProduct.id == mold_product_id) \
        .first()

    if not record:
        raise HTTPException(status_code=404, detail="Mold-Product not found")
    return record


@router.put("/{mold_product_id}", response_model=MoldProductOut)
def update_mold_product(mold_product_id: int, data: MoldProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mold = db.query(Mold).filter(Mold.factory_id == current_user.factory_id, Mold.id == data.mold_id).first()
    product = db.query(Product).filter(Product.factory_id == current_user.factory_id, Product.id == data.product_id).first()

    if not mold or not product:
        raise HTTPException(status_code=400, detail="Mold or Product not found.")

    record = db.query(MoldProduct).filter(MoldProduct.id == mold_product_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Mold-Product not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mold-Product pair already exists.")
    
    return record


@router.delete("/{mold_product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mold_product(mold_product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(MoldProduct) \
        .join(Mold, Mold.id == MoldProduct.mold_id) \
        .join(Product, Product.id == MoldProduct.product_id) \
        .filter(Mold.factory_id == current_user.factory_id) \
        .filter(Product.factory_id == current_user.factory_id) \
        .filter(MoldProduct.id == mold_product_id) \
        .first()

    if not record:
        raise HTTPException(status_code=404, detail="Mold-Product not found")

    db.delete(record)
    db.commit()
