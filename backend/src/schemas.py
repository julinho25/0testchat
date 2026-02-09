from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel
from .models import UserRole, VehicleType, VehicleStatus, DeliveryStatus, RouteJobStatus, ShiftType


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole

    class Config:
        orm_mode = True


class VehicleOut(BaseModel):
    id: str
    plate: str
    vehicle_type: VehicleType
    status: VehicleStatus
    capacity_kg: Optional[float]
    tags: Optional[List[str]]

    class Config:
        orm_mode = True


class ClientOut(BaseModel):
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    address_count: int

    class Config:
        orm_mode = True


class DeliveryOut(BaseModel):
    id: str
    order_id: str
    client_name: str
    status: DeliveryStatus
    weight_kg: Optional[float]
    revenue_expected: Optional[float]

    class Config:
        orm_mode = True


class RouteJobOut(BaseModel):
    id: str
    status: RouteJobStatus

    class Config:
        orm_mode = True


class RouteResultOut(BaseModel):
    routes: List[dict]


class Pagination(BaseModel):
    items: List
    totalCount: int


class RouteJobCreate(BaseModel):
    depot_id: str
    route_date: date
    shift: ShiftType
    delivery_ids: List[str]
    vehicle_ids: List[str]
    config: dict


class DashboardResponse(BaseModel):
    kpis: dict
    daily: List[dict]
    top_clients: List[dict]
    invoices: List[dict]
