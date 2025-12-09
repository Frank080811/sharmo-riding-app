# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from auth import router as auth_router, get_current_user
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router

# IMPORTANT: Create all DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shamor Ride API")

# CORS for your frontend
origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "*",   # allow for testing (optional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rides_router, prefix="/rides", tags=["Rides"])
app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


# -------------------------
# FIX: Missing profile endpoint
# -------------------------
@app.get("/auth/me")
def get_profile(user=Depends(get_current_user)):
    """
    Returns user info so frontend can store profile.
    """
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": user.created_at,
    }


@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running"}
