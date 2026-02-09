import os
from datetime import datetime
from celery import Celery
import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import RouteJob, RouteJobStatus, Delivery, Vehicle, Route

celery = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

OSRM_URL = os.getenv("OSRM_URL", "http://osrm:5000")


def _osrm_table(coords):
    coord_str = ";".join([f"{lng},{lat}" for lat, lng in coords])
    response = requests.get(f"{OSRM_URL}/table/v1/driving/{coord_str}?annotations=duration,distance", timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["durations"], data["distances"]


def _solve_vrp(dist_matrix):
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(dist_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        return []
    index = routing.Start(0)
    order = []
    while not routing.IsEnd(index):
        order.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    return order


@celery.task
def create_route_job(job_id: str, payload: dict):
    db: Session = SessionLocal()
    job = db.query(RouteJob).filter(RouteJob.id == job_id).first()
    if not job:
        return
    try:
        job.status = RouteJobStatus.running
        job.started_at = datetime.utcnow()
        db.commit()

        deliveries = db.query(Delivery).filter(Delivery.status == "pending").limit(25).all()
        if not deliveries:
            job.status = RouteJobStatus.done
            job.finished_at = datetime.utcnow()
            db.commit()
            return
        coords = [(d.lat, d.lng) for d in deliveries]
        durations, distances = _osrm_table(coords)
        order = _solve_vrp(distances)

        vehicle = db.query(Vehicle).first()
        total_km = sum(distances[order[i]][order[i + 1]] for i in range(len(order) - 1)) / 1000
        total_time = sum(durations[order[i]][order[i + 1]] for i in range(len(order) - 1)) / 60
        cost_km = total_km * ((vehicle.cost_per_km if vehicle else 1.5) or 1.5)
        cost_hour = total_time * ((vehicle.cost_per_hour if vehicle else 80) or 80)
        cost_fuel = total_km / ((vehicle.km_per_liter if vehicle else 6) or 6) * payload.get("config", {}).get("fuel_price", 6)
        cost_fixed = (vehicle.fixed_cost_value if vehicle else 0) or 0
        cost_total = cost_km + cost_hour + cost_fuel + cost_fixed

        route = Route(
            route_job_id=job.id,
            vehicle_id=vehicle.id if vehicle else None,
            total_km=total_km,
            total_time_min=total_time,
            cost_km=cost_km,
            cost_hour=cost_hour,
            cost_fuel=cost_fuel,
            cost_fixed=cost_fixed,
            cost_total=cost_total,
            baseline_cost_total=cost_total * 1.1,
            savings_value=cost_total * 0.1,
            polyline_geojson=None,
        )
        db.add(route)
        job.status = RouteJobStatus.done
        job.finished_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        job.status = RouteJobStatus.failed
        job.error_message = str(exc)
        job.finished_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()
