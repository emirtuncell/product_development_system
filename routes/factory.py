from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Factory, User
from schemas import FactoryCreate, FactoryUpdate, FactoryOut
from auth import get_superuser

router = APIRouter(prefix="/factories", tags=["factories"])

@router.post("/", response_model=FactoryOut, status_code=status.HTTP_201_CREATED)
def create_factory(data: FactoryCreate, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    factory = Factory(**data.dict())
    db.add(factory)
    db.commit()
    db.refresh(factory)
    return factory

@router.get("/", response_model=List[FactoryOut])
def list_factories(db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    return db.query(Factory).all()

@router.get("/{factory_id}", response_model=FactoryOut)
def get_factory(factory_id: int, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    return factory

@router.put("/{factory_id}", response_model=FactoryOut)
def update_factory(factory_id: int, data: FactoryUpdate, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(factory, key, value)

    db.commit()
    db.refresh(factory)
    return factory

@router.delete("/{factory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factory(factory_id: int, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    db.delete(factory)
    db.commit()
