import csv
import io
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from ..deps import get_db, require_role
from ..models import Vehicle, UserRole

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/")
def list_vehicles(
    status: str = "",
    type: str = "",
    tag: str = "",
    page: int = 1,
    pageSize: int = 20,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin, UserRole.operacao)),
):
    query = db.query(Vehicle)
    if status:
        query = query.filter(Vehicle.status == status)
    if type:
        query = query.filter(Vehicle.vehicle_type == type)
    if tag:
        query = query.filter(Vehicle.tags.contains([tag]))
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()
    return {"items": items, "totalCount": total}


@router.post("/import")
def import_vehicles(file: UploadFile, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin))):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    errors = []
    for row in reader:
        try:
            vehicle = Vehicle(
                plate=row["plate"],
                vehicle_type=row.get("vehicle_type", "VAN"),
                capacity_kg=float(row.get("capacity_kg") or 0),
                status=row.get("status", "active"),
                tags=(row.get("tags") or "").split(";") if row.get("tags") else [],
            )
            db.add(vehicle)
            imported += 1
        except Exception as exc:
            errors.append({"row": row, "error": str(exc)})
    db.commit()
    return {"imported": imported, "errors": errors}
