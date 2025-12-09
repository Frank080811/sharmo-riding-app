# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, get_db
import models

# Routers
from auth import router as auth_router, get_current_user
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router


# ------------------------------------------------------
# IMPORTANT: Create all PostgreSQL tables ON STARTUP
# ------------------------------------------------------
def create_tables():
    """
    Ensure all tables exist in the PostgreSQL database.
    Render requires tables to be created programmatically.
    """
    print("🔵 Creating database tables (if not exists)...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready.")


# ------------------------------------------------------
# FastAPI App
# ------------------------------------------------------
app = FastAPI(title="Shamor Ride API")


# ------------------------------------------------------
# CORS (Accept Frontend + Mobile + Direct Testing)
# ------------------------------------------------------
origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "https://shamor-riding-frontend.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "*",  # Allow temporarily for testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------
# STARTUP EVENT (Runs Once on Render Deployment)
# ------------------------------------------------------
@app.on_event("startup")
def on_startup():
    create_tables()


# ------------------------------------------------------
# Include Routers
# ------------------------------------------------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rides_router, prefix="/rides", tags=["Rides"])
app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


# ------------------------------------------------------
# FIXED — Missing Profile Endpoint
# ------------------------------------------------------
@app.get("/auth/me")
def get_profile(user=Depends(get_current_user)):
    """
    Used by frontend after login.
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
    return {"status": "Shamor-Ride backend running 🚀"}
