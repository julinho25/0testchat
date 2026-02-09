import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import Depot, Vehicle, Client, ClientAddress, Delivery, Invoice, Payment, User
from src.auth import hash_password

random.seed(42)


def seed():
    db: Session = SessionLocal()
    if db.query(User).first():
        print("Seed já executado.")
        return

    admin = User(name="Admin", email="admin@logiflow.com", password_hash=hash_password("admin123"), role="Admin")
    db.add(admin)

    depots = []
    for i in range(3):
        depot = Depot(name=f"Base {i+1}", lat=-23.55 + i * 0.05, lng=-46.63 + i * 0.05, address="São Paulo")
        depots.append(depot)
        db.add(depot)

    vehicles = []
    for i in range(50):
        vehicle = Vehicle(
            plate=f"ABC{i:04d}",
            vehicle_type=random.choice(["VAN", "TRUCK", "CARRO", "VUC"]),
            capacity_kg=random.randint(500, 5000),
            status=random.choice(["active", "maintenance", "inactive"]),
            km_per_liter=random.uniform(4, 8),
            cost_per_km=random.uniform(1.2, 2.5),
            cost_per_hour=random.uniform(60, 110),
            fixed_cost_value=random.uniform(200, 800),
        )
        vehicles.append(vehicle)
        db.add(vehicle)

    clients = []
    for i in range(200):
        client = Client(name=f"Cliente {i+1}", email=f"cliente{i+1}@mail.com", phone="119999999")
        db.add(client)
        clients.append(client)
    db.flush()

    addresses = []
    for client in clients:
        for _ in range(random.randint(1, 3)):
            address = ClientAddress(
                client_id=client.id,
                label="Matriz",
                street="Rua Exemplo",
                number=str(random.randint(1, 999)),
                city="São Paulo",
                state="SP",
                zip="01000-000",
                lat=-23.55 + random.uniform(-0.1, 0.1),
                lng=-46.63 + random.uniform(-0.1, 0.1),
                geocode_source="manual",
            )
            addresses.append(address)
            db.add(address)
    db.flush()

    for i in range(2000):
        address = random.choice(addresses)
        delivery = Delivery(
            order_id=f"ORD-{i+1:05d}",
            client_id=address.client_id,
            address_id=address.id,
            lat=address.lat,
            lng=address.lng,
            weight_kg=random.uniform(5, 200),
            volume_m3=random.uniform(0.1, 2.0),
            revenue_expected=random.uniform(50, 500),
            status=random.choice(["pending", "routed", "delivered"]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.add(delivery)

    for client in clients[:50]:
        invoice = Invoice(
            client_id=client.id,
            month_ref=datetime.utcnow().strftime("%Y-%m"),
            amount_expected=random.uniform(1000, 8000),
            status=random.choice(["open", "paid"]),
            due_date=datetime.utcnow().date() + timedelta(days=15),
        )
        db.add(invoice)
        if invoice.status == "paid":
            payment = Payment(
                invoice_id=invoice.id,
                paid_at=datetime.utcnow(),
                amount=invoice.amount_expected,
                method="PIX",
            )
            db.add(payment)

    db.commit()
    print("Seed completo")


if __name__ == "__main__":
    seed()
