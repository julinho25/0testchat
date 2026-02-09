import csv
import io
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from ..deps import get_db, require_role
from ..models import Delivery, Client, UserRole

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("/")
def list_deliveries(status: str = "", order_id: str = "", page: int = 1, pageSize: int = 20, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    query = db.query(Delivery)
    if status:
        query = query.filter(Delivery.status == status)
    if order_id:
        query = query.filter(Delivery.order_id.ilike(f"%{order_id}%"))
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()
    data = []
    for delivery in items:
        data.append({
            "id": str(delivery.id),
            "order_id": delivery.order_id,
            "client_name": delivery.client.name if delivery.client else "",
            "status": delivery.status,
            "weight_kg": delivery.weight_kg,
            "revenue_expected": float(delivery.revenue_expected or 0),
        })
    return {"items": data, "totalCount": total}


@router.post("/import")
def import_deliveries(file: UploadFile, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    for row in reader:
        client = db.query(Client).filter(Client.name == row.get("client")).first()
        delivery = Delivery(
            order_id=row["order_id"],
            client_id=client.id if client else None,
            lat=float(row.get("lat") or 0),
            lng=float(row.get("lng") or 0),
            weight_kg=float(row.get("weight_kg") or 0),
            volume_m3=float(row.get("volume_m3") or 0),
            revenue_expected=float(row.get("revenue_expected") or 0),
        )
        db.add(delivery)
        imported += 1
    db.commit()
    return {"imported": imported}
