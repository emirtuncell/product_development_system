from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import User, UserType
from database import get_db
from schemas import FactoryUserCreate, FactoryUserUpdate, UserOut
from auth import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: FactoryUserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_user = User(**user.dict(),factory_id=current_user.factory_id)
    db_user.password=get_password_hash(db_user.password)
    if user.user_type==UserType.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(User).filter(User.factory_id==current_user.factory_id).all()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id, User.factory_id==current_user.factory_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, update_data: FactoryUserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id,User.factory_id==current_user.factory_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
        if key=="password":
            user.password=get_password_hash(user.password)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id,User.factory_id==current_user.factory_id).first()
    if user.id==current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
