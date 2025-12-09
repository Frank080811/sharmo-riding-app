from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class UserRole(str, enum.Enum):
    rider = "rider"
    driver = "driver"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)   # <-- correct
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.rider)
    is_active = Column(Boolean, default=True)
    rating = Column(Float, default=5.0)


    rides_as_rider = relationship("Ride", foreign_keys="Ride.rider_id", back_populates="rider")
    rides_as_driver = relationship("Ride", foreign_keys="Ride.driver_id", back_populates="driver")
    wallet = relationship("Wallet", back_populates="user", uselist=False)


class RideStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)

    rider_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    pickup = Column(String, nullable=False)
    dropoff = Column(String, nullable=False)
    ride_type = Column(String, default="standard")
    payment_method = Column(String, default="cash")
    promo_code = Column(String, nullable=True)

    distance_km = Column(Float, default=0)
    duration_min = Column(Float, default=0)
    fare = Column(Float, default=0)

    status = Column(Enum(RideStatus), default=RideStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    rider = relationship("User", foreign_keys=[rider_id], back_populates="rides_as_rider")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="rides_as_driver")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float, default=0)

    user = relationship("User", back_populates="wallet")
