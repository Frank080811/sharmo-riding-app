from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Ride


def get_city_heatmap(db: Session):
    last10 = datetime.utcnow() - timedelta(minutes=10)
    rides = db.query(Ride).filter(Ride.created_at >= last10).all()

    heat = {}
    for r in rides:
        zone = f"{round(r.distance_km or 0)}km-radius"
        heat[zone] = heat.get(zone, 0) + 1
    return heat


def compute_surge(heat: dict) -> float:
    if not heat:
        return 1.0
    max_load = max(heat.values())
    multiplier = 1 + (max_load / 10)
    return min(multiplier, 3.0)
