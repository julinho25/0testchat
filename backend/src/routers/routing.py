from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from ..deps import get_db, require_role
from ..models import RouteJob, RouteJobStatus, UserRole, Route
from ..schemas import RouteJobCreate
from ..worker import create_route_job

router = APIRouter(prefix="/routing", tags=["routing"])


@router.post("/jobs")
def create_job(payload: RouteJobCreate, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    job = RouteJob(
        depot_id=payload.depot_id,
        shift=payload.shift,
        route_date=payload.route_date,
        status=RouteJobStatus.queued,
        config=payload.config,
        created_by=user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    create_route_job.delay(str(job.id), payload.dict())
    return {"id": str(job.id), "status": job.status}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    job = db.query(RouteJob).filter(RouteJob.id == job_id).first()
    return {"id": str(job.id), "status": job.status, "error": job.error_message}


@router.get("/jobs/{job_id}/result")
def get_result(job_id: str, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    routes = db.query(Route).filter(Route.route_job_id == job_id).all()
    return {
        "routes": [
            {
                "id": str(route.id),
                "vehicle_id": str(route.vehicle_id),
                "total_km": route.total_km,
                "total_time_min": route.total_time_min,
                "cost_total": route.cost_total,
                "polyline_geojson": route.polyline_geojson,
            }
            for route in routes
        ]
    }


@router.get("/routes/{route_id}/export")
def export_route(route_id: str, format: str = "csv", db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin, UserRole.operacao))):
    route = db.query(Route).filter(Route.id == route_id).first()
    if format == "csv":
        content = "route_id,total_km,total_time_min,cost_total\n"
        content += f\"{route.id},{route.total_km},{route.total_time_min},{route.cost_total}\\n\"
        return Response(content, media_type=\"text/csv\")
    return {\"message\": \"PDF simples disponível em evolução\"}
