from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/rides", tags=["Rides"])


@router.post("")
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
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return ride
