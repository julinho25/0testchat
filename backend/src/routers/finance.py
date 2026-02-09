from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..deps import get_db, require_role
from ..models import Invoice, Payment, Delivery, Client, UserRole, Route

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/dashboard")
def finance_dashboard(month: str, page: int = 1, pageSize: int = 20, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.financeiro, UserRole.leitura))):
    invoices_query = db.query(Invoice).filter(Invoice.month_ref == month)
    total_cost = db.query(func.sum(Route.cost_total)).scalar() or 0
    total_expected = db.query(func.sum(Invoice.amount_expected)).scalar() or 0
    received_month = db.query(func.sum(Payment.amount)).filter(func.to_char(Payment.paid_at, 'YYYY-MM') == month).scalar() or 0

    daily = []
    for day in range(1, 29):
        daily.append({"day": f"{day:02d}", "cost": float(total_cost) / 28, "received": float(received_month) / 28})

    top_clients = db.query(Client.name, func.sum(Invoice.amount_expected)).join(Invoice, Invoice.client_id == Client.id).group_by(Client.name).limit(10).all()
    top_data = [{"client": name, "revenue": float(value or 0), "cost": float(value or 0) * 0.6} for name, value in top_clients]

    invoices = invoices_query.offset((page - 1) * pageSize).limit(pageSize).all()
    invoice_list = [{"client": inv.client_id, "amount": float(inv.amount_expected or 0), "status": inv.status, "due_date": inv.due_date} for inv in invoices]

    return {
        "kpis": {
            "cost_total": float(total_cost),
            "to_receive": float(total_expected - received_month),
            "received_month": float(received_month),
            "savings": float(total_cost) * 0.08,
        },
        "daily": daily,
        "top_clients": top_data,
        "invoices": invoice_list,
    }


@router.post("/payments")
def add_payment(payload: dict, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.financeiro))):
    payment = Payment(**payload)
    db.add(payment)
    db.commit()
    return payment


@router.get("/payments")
def list_payments(page: int = 1, pageSize: int = 20, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.financeiro))):
    query = db.query(Payment)
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()
    return {"items": items, "totalCount": total}


@router.get("/export")
def export_finance():
    return {"message": "Exportação disponível via CSV/XLSX no front-end."}
