# rides.py
# LOGIN VALIDATION (fixed — no emojis)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/rides", tags=["rides"])


@router.post("/", summary="Create a ride request")
def create_ride(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ride = models.Ride(
        rider_id=user.id,
        pickup=payload["pickup"],
        dropoff=payload["dropoff"],
        ride_type=payload.get("ride_type", "standard"),
        payment_method=payload.get("payment_method", "cash"),
        promo_code=payload.get("promo_code"),
        distance_km=payload.get("distance_km", 0),
        duration_min=payload.get("duration_min", 0),
        fare=payload.get("fare", 0),
        created_at=datetime.utcnow(),
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return ride


@router.get("/my", summary="Get all rides for current user")
def my_rides(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Ride).filter(models.Ride.rider_id == user.id).all()


@router.post("/{ride_id}/accept", summary="Driver accepts a ride")
def accept_ride(ride_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")

    if user.role != models.UserRole.driver:
        raise HTTPException(403, "Only drivers can accept rides")

    ride.driver_id = user.id
    ride.status = models.RideStatus.accepted

    db.commit()
    db.refresh(ride)
    return ride


@router.post("/{ride_id}/complete", summary="Driver completes a ride")
def complete_ride(ride_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")

    ride.status = models.RideStatus.completed
    db.commit()
    return ride
