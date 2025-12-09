# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

# Routers
from auth import router as auth_router, get_current_user
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router

# Initialize the app
app = FastAPI(title="Shamor Ride API")

# CORS configuration
origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "*",  # development fallback
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure PostgreSQL tables are created on startup
@app.on_event("startup")
def on_startup():
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rides_router, prefix="/rides", tags=["Rides"])
app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# AUTH PROFILE ENDPOINT (fix for /auth/me)
@app.get("/auth/me")
def get_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": user.created_at,
    }

# Root
@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running with PostgreSQL"}
