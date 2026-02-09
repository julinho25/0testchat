from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, require_role
from ..models import AuditLog, UserRole

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/")
def list_audit(page: int = 1, pageSize: int = 20, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin))):
    query = db.query(AuditLog)
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()
    return {"items": items, "totalCount": total}
