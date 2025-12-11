# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

# Routers
from auth import router as auth_router
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router
from realtime import router as ws_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Shamor Ride API")

# -------------------------------------------------------------
# ✅ FIXED CORS — "*" CANNOT BE USED WITH allow_credentials=True
# -------------------------------------------------------------
allowed_origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "http://starmo-ride-frontend.onrender.com",
    "http://localhost:5500",            # allow local testing
    "http://127.0.0.1:5500",
    "https://sharmo-ride-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,        # requires explicit origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# DATABASE INIT
# -------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("Creating PostgreSQL tables…")
    Base.metadata.create_all(bind=engine)
    print("Done.")


# -------------------------------------------------------------
# ROUTERS
# -------------------------------------------------------------
# Prefixes are already inside each router → do not add prefixes here.
app.include_router(auth_router)       # /auth
app.include_router(rides_router)      # /rides
app.include_router(wallet_router)     # /wallet
app.include_router(admin_router)      # /admin
app.include_router(ws_router)         # /ws


# -------------------------------------------------------------
# ROOT ENDPOINT
# -------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running with PostgreSQL"}
