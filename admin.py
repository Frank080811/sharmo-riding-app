# admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
import models
import schemas
from auth import get_current_admin
from surge import get_city_heatmap, compute_surge

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=schemas.AdminOverviewOut)
def overview(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)

    rides = db.query(models.Ride).filter(models.Ride.created_at >= last_24h).all()
    rides_24h = len(rides)
    revenue_24h = sum(r.fare or 0 for r in rides)

    drivers = db.query(models.User).filter(models.User.role == models.UserRole.driver).count()

    hourly_counts = [0] * 24
    for r in rides:
        h = r.created_at.hour
        hourly_counts[h] += 1

    hourly_hours = list(range(24))

    return schemas.AdminOverviewOut(
        rides_24h=rides_24h,
        revenue_24h=revenue_24h,
        active_drivers=drivers,
        hourly_hours=hourly_hours,
        hourly_counts=hourly_counts,
    )


@router.get("/heatmap", response_model=schemas.HeatmapOut)
def heatmap(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    heat = get_city_heatmap(db)
    surge = compute_surge(heat)
    return schemas.HeatmapOut(heat=heat, surge=surge)


@router.get("/heatmap/surge")
def heatmap_surge(db: Session = Depends(get_db)):
    heat = get_city_heatmap(db)
    surge = compute_surge(heat)
    return {"multiplier": surge}


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    users = db.query(models.User).all()
    return users
