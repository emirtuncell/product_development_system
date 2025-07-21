from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import User
from database import get_db
from schemas import UserLogin, Token, UserOut
from auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def test_token(current_user: User = Depends(get_current_user)):
    """
    Token'ın geçerli olup olmadığını test etmek için endpoint
    """
    return current_user