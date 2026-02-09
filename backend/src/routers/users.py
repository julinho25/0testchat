from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user, require_role
from ..models import User, UserRole
from ..auth import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/")
def list_users(db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.admin))):
    return db.query(User).all()


@router.post("/")
def create_user(payload: dict, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.admin))):
    new_user = User(
        name=payload["name"],
        email=payload["email"],
        password_hash=hash_password(payload["password"]),
        role=payload.get("role", UserRole.operacao),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/{user_id}/reset-password")
def reset_password(user_id: str, payload: dict, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.admin))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    target.password_hash = hash_password(payload["password"])
    db.commit()
    return {"message": "Senha atualizada"}
