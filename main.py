from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, get_db
import models
import schemas
import auth
import realtime
import surge
import verify
import admin as admin_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftRide API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(realtime.router)
app.include_router(verify.router)
app.include_router(admin_routes.router)


@app.post("/auth/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = get_db()):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=auth.hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if not user.wallet:
        wallet = models.Wallet(user_id=user.id, balance=0.0)
        db.add(wallet)
        db.commit()

    return user


@app.post("/auth/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = get_db(),
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/wallet/topup", response_model=schemas.WalletOut)
def topup_wallet(
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = models.Wallet(user_id=current_user.id, balance=0.0)
        db.add(wallet)
    wallet.balance += 20.0
    db.commit()
    db.refresh(wallet)
    return schemas.WalletOut(balance=wallet.balance)


@app.get("/wallet/me", response_model=schemas.WalletOut)
def get_wallet(
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = models.Wallet(user_id=current_user.id, balance=0.0)
        db.add(wallet)
        db.commit()
    return schemas.WalletOut(balance=wallet.balance)


@app.post("/rides", response_model=schemas.RideOut)
async def create_ride(
    ride_in: schemas.RideCreate,
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role != models.UserRole.rider:
        raise HTTPException(status_code=403, detail="Only riders can create rides")

    distance_km = 5.0
    duration_min = 15.0

    heat = surge.get_city_heatmap(db)
    surge_multiplier = surge.compute_surge(heat)

    fare = (5 + distance_km * 0.6 + duration_min * 0.12) * surge_multiplier

    if ride_in.payment_method == "wallet":
        wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
        if not wallet or wallet.balance < fare:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        wallet.balance -= fare
        db.add(wallet)

    ride = models.Ride(
        rider_id=current_user.id,
        pickup=ride_in.pickup,
        dropoff=ride_in.dropoff,
        ride_type=ride_in.ride_type,
        payment_method=ride_in.payment_method,
        promo_code=ride_in.promo_code,
        distance_km=distance_km,
        duration_min=duration_min,
        fare=fare,
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)

    await realtime.broadcast_ride_request({
        "id": ride.id,
        "pickup": ride.pickup,
        "dropoff": ride.dropoff,
        "distance_km": ride.distance_km,
        "fare": ride.fare,
    })

    return ride


@app.get("/rides/my", response_model=List[schemas.RideOut])
def my_rides(
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    q = db.query(models.Ride)
    if current_user.role == models.UserRole.rider:
        q = q.filter(models.Ride.rider_id == current_user.id)
    elif current_user.role == models.UserRole.driver:
        q = q.filter(models.Ride.driver_id == current_user.id)
    return q.order_by(models.Ride.created_at.desc()).limit(50).all()


@app.post("/rides/{ride_id}/accept", response_model=schemas.RideOut)
async def accept_ride(
    ride_id: int,
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role != models.UserRole.driver:
        raise HTTPException(status_code=403, detail="Only drivers can accept rides")

    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.status != models.RideStatus.pending:
        raise HTTPException(status_code=400, detail="Ride not pending")

    ride.driver_id = current_user.id
    ride.status = models.RideStatus.accepted
    db.commit()
    db.refresh(ride)

    await realtime.broadcast_ride_status(ride.id, ride.status.value, current_user.full_name or current_user.email)
    return ride


@app.post("/rides/{ride_id}/complete", response_model=schemas.RideOut)
async def complete_ride(
    ride_id: int,
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if current_user.role not in (models.UserRole.driver, models.UserRole.admin):
        raise HTTPException(status_code=403, detail="Not allowed")
    ride.status = models.RideStatus.completed
    db.commit()
    db.refresh(ride)

    await realtime.broadcast_ride_status(ride.id, ride.status.value)
    return ride


@app.post("/rides/{ride_id}/rate", response_model=schemas.RatingOut)
def rate_ride(
    ride_id: int,
    rating_in: schemas.RatingCreate,
    db: Session = get_db(),
    current_user: models.User = Depends(auth.get_current_user),
):
    ride = db.query(models.Ride).filter(models.Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.rider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the rider can rate this ride")

    rating = models.Rating(
        ride_id=ride.id,
        driver_id=ride.driver_id,
        rider_id=current_user.id,
        stars=rating_in.stars,
        comment=rating_in.comment,
    )
    db.add(rating)

    driver = db.query(models.User).filter(models.User.id == ride.driver_id).first()
    if driver:
        ratings = db.query(models.Rating).filter(models.Rating.driver_id == driver.id).all()
        if ratings:
            driver.rating = sum(r.stars for r in ratings) / len(ratings)
            db.add(driver)

    db.commit()
    db.refresh(rating)
    return rating
