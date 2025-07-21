from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Mold
from database import get_db
from schemas import MoldCreate, MoldUpdate, MoldOut
from auth import get_current_user

router = APIRouter(prefix="/molds", tags=["molds"])

@router.post("/", response_model=MoldOut, status_code=status.HTTP_201_CREATED)
def create_mold(mold: MoldCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        db_mold = Mold(**mold.dict(),factory_id=current_user.factory_id)
        db.add(db_mold)
        db.commit()
        db.refresh(db_mold)
        return db_mold
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=List[MoldOut])
def list_molds(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Mold).filter(Mold.is_deleted == False,Mold.factory_id==current_user.factory_id).all()

@router.get("/{mold_id}", response_model=MoldOut)
def get_mold(mold_id: int, db: Session = Depends(get_db), current_user=Depends         (get_current_user)):
    try:
        mold = db.query(Mold).filter(Mold.id == mold_id, Mold.is_deleted == False,Mold. factory_id==current_user.factory_id).first()
        if not mold:
            raise HTTPException(status_code=404, detail="Mold not found")
        return mold
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{mold_id}", response_model=MoldOut)
def update_mold(mold_id: int, update_data: MoldUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        mold = db.query(Mold).filter(Mold.id == mold_id,Mold.factory_id==current_user.factory_id).first()
        if not mold:
            raise HTTPException(status_code=404, detail="Mold not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(mold, key, value)
        db.commit()
        db.refresh(mold)
        return mold

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{mold_id}", status_code=status.HTTP_204_NO_CONTENT)

def soft_delete_mold(mold_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mold = db.query(Mold).filter(Mold.id == mold_id,Mold.factory_id==current_user.factory_id).first()
    if not mold:
        raise HTTPException(status_code=404, detail="Mold not found")
    mold.is_deleted = True
    db.commit()
