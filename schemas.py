from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole, RideStatus


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole


class UserOut(UserBase):
    id: int
    role: UserRole
    rating: float

    class Config:
        orm_mode = True


class RideCreate(BaseModel):
    pickup: str
    dropoff: str
    ride_type: str = "standard"
    payment_method: str = "cash"
    promo_code: Optional[str] = None


class RideOut(BaseModel):
    id: int
    pickup: str
    dropoff: str
    ride_type: str
    payment_method: str
    distance_km: float
    duration_min: float
    fare: float
    status: RideStatus
    created_at: datetime

    class Config:
        orm_mode = True


class WalletOut(BaseModel):
    balance: float

    class Config:
        orm_mode = True


class RatingCreate(BaseModel):
    stars: float
    comment: Optional[str] = None


class RatingOut(BaseModel):
    id: int
    ride_id: int
    driver_id: int
    rider_id: int
    stars: float
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class AdminOverviewOut(BaseModel):
    rides_24h: int
    revenue_24h: float
    active_drivers: int
    hourly_hours: List[int]
    hourly_counts: List[int]


class HeatmapOut(BaseModel):
    heat: dict
    surge: float
