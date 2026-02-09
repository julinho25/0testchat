from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User
from ..auth import verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    email: str
    password: str


class RefreshInput(BaseModel):
    refreshToken: str


@router.post("/login")
def login(payload: LoginInput):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {
        "accessToken": create_access_token(str(user.id)),
        "refreshToken": create_refresh_token(str(user.id)),
    }


@router.post("/refresh")
def refresh(payload: RefreshInput):
    user_id = decode_token(payload.refreshToken)
    if not user_id:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    return {
        "accessToken": create_access_token(user_id),
        "refreshToken": payload.refreshToken,
    }


@router.post("/logout")
def logout():
    return {"message": "Logout efetuado"}
