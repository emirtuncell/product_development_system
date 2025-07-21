from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Product
from database import get_db
from schemas import ProductCreate, ProductUpdate, ProductOut
from auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        db_product = Product(**product.dict(), factory_id=current_user.factory_id)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Product).filter(Product.is_deleted == False, Product.factory_id==current_user.factory_id).all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_deleted == False, Product.factory_id==current_user.factory_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, update_data: ProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        product = db.query(Product).filter(Product.id == product_id, Product.factory_id==current_user.factory_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.factory_id==current_user.factory_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_deleted = True
    db.commit()
