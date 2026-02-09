import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    Boolean,
    Numeric,
    Integer,
    Float,
    ForeignKey,
    Text,
    Date,
    Time,
    JSON,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .database import Base


class UserRole(str, enum.Enum):
    admin = "Admin"
    operacao = "Operacao"
    financeiro = "Financeiro"
    leitura = "Leitura"


class VehicleType(str, enum.Enum):
    VAN = "VAN"
    VUC = "VUC"
    TRUCK = "TRUCK"
    CARRETA = "CARRETA"
    CARRO = "CARRO"
    AGREGADO = "AGREGADO"
    OUTRO = "OUTRO"


class VehicleStatus(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    inactive = "inactive"


class DeliveryStatus(str, enum.Enum):
    pending = "pending"
    routed = "routed"
    on_route = "on_route"
    delivered = "delivered"
    canceled = "canceled"


class RouteJobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class ShiftType(str, enum.Enum):
    morning = "morning"
    afternoon = "afternoon"
    night = "night"


class AuditAction(str, enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"
    import_action = "import"
    route_optimize = "route_optimize"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Depot(Base):
    __tablename__ = "depots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    address = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate = Column(String, unique=True, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    capacity_kg = Column(Float)
    capacity_m3 = Column(Float)
    height_m = Column(Float)
    width_m = Column(Float)
    length_m = Column(Float)
    tare_kg = Column(Float)
    max_stops = Column(Integer)
    start_depot_id = Column(UUID(as_uuid=True), ForeignKey("depots.id"))
    end_depot_id = Column(UUID(as_uuid=True), ForeignKey("depots.id"))
    shift_start = Column(Time)
    shift_end = Column(Time)
    tags = Column(ARRAY(String), default=[])
    status = Column(Enum(VehicleStatus), default=VehicleStatus.active)
    km_per_liter = Column(Float)
    fixed_cost_period = Column(String)
    fixed_cost_value = Column(Float)
    cost_per_km = Column(Float)
    cost_per_hour = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    start_depot = relationship("Depot", foreign_keys=[start_depot_id])
    end_depot = relationship("Depot", foreign_keys=[end_depot_id])


class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    cpf_cnpj = Column(String)
    phone = Column(String)
    email = Column(String)
    commercial_terms = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    addresses = relationship("ClientAddress", back_populates="client", cascade="all, delete-orphan")


class ClientAddress(Base):
    __tablename__ = "client_addresses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    label = Column(String)
    street = Column(String)
    number = Column(String)
    district = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    geocode_source = Column(String)
    restrictions = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="addresses")


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, unique=True, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("client_addresses.id"))
    lat = Column(Float)
    lng = Column(Float)
    weight_kg = Column(Float)
    volume_m3 = Column(Float)
    time_window_start = Column(Time)
    time_window_end = Column(Time)
    revenue_expected = Column(Numeric(12, 2))
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.pending)
    routed_job_id = Column(UUID(as_uuid=True), ForeignKey("route_jobs.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    client = relationship("Client")
    address = relationship("ClientAddress")


class RouteJob(Base):
    __tablename__ = "route_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    depot_id = Column(UUID(as_uuid=True), ForeignKey("depots.id"), nullable=False)
    shift = Column(Enum(ShiftType), nullable=False)
    route_date = Column(Date, nullable=False)
    status = Column(Enum(RouteJobStatus), default=RouteJobStatus.queued)
    config = Column(JSON)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    error_message = Column(Text)

    depot = relationship("Depot")


class Route(Base):
    __tablename__ = "routes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_job_id = Column(UUID(as_uuid=True), ForeignKey("route_jobs.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"))
    total_km = Column(Float)
    total_time_min = Column(Float)
    cost_fuel = Column(Float)
    cost_km = Column(Float)
    cost_hour = Column(Float)
    cost_fixed = Column(Float)
    cost_total = Column(Float)
    baseline_cost_total = Column(Float)
    savings_value = Column(Float)
    polyline_geojson = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    vehicle = relationship("Vehicle")
    job = relationship("RouteJob")


class RouteStop(Base):
    __tablename__ = "route_stops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False)
    stop_sequence = Column(Integer, nullable=False)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=False)
    eta = Column(DateTime)
    service_time_min = Column(Integer, default=5)
    created_at = Column(DateTime, server_default=func.now())


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    month_ref = Column(String, nullable=False)
    amount_expected = Column(Numeric(12, 2))
    status = Column(String)
    due_date = Column(Date)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"))
    paid_at = Column(DateTime)
    amount = Column(Numeric(12, 2))
    method = Column(String)
    notes = Column(Text)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    entity = Column(String)
    entity_id = Column(UUID(as_uuid=True))
    action = Column(Enum(AuditAction))
    before = Column(JSON)
    after = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    ip = Column(String)
    user_agent = Column(String)
