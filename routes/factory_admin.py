from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, User, UserType
from schemas import UserCreate, UserUpdate, UserOut
from auth import get_superuser, get_password_hash

router = APIRouter(prefix="/factory-admins", tags=["factory_admins"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    user = User(**data.dict())
    user.password=get_password_hash(user.password)
    user.user_type=UserType.factory_admin
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{factory_id}", response_model=List[UserOut])
def list_users(factory_id:int,db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    return db.query(User).filter(User.factory_id==factory_id).all()


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
        if key=="password":
            user.password=get_password_hash(user.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), admin:User=Depends(get_superuser)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
