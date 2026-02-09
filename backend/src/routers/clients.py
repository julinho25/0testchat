import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, require_role
from ..models import Client, ClientAddress, UserRole

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/")
def list_clients(search: str = "", page: int = 1, pageSize: int = 20, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    query = db.query(Client)
    if search:
        query = query.filter(Client.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()
    data = []
    for client in items:
        data.append({
            "id": str(client.id),
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "address_count": len(client.addresses),
        })
    return {"items": data, "totalCount": total}


@router.post("/")
def create_client(payload: dict, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    client = Client(**payload)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.post("/{client_id}/addresses")
def add_address(client_id: str, payload: dict, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    address = ClientAddress(client_id=client_id, **payload)
    if not address.lat or not address.lng:
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"format": "json", "q": f"{address.street} {address.number}, {address.city}"},
            headers={"User-Agent": "logiflow"},
            timeout=10,
        ).json()
        if geo:
            address.lat = float(geo[0]["lat"])
            address.lng = float(geo[0]["lon"])
            address.geocode_source = "provider"
    db.add(address)
    db.commit()
    return address
