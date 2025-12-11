# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import Base, engine
import models

# Routers
from auth import router as auth_router
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router
from realtime import router as ws_router

load_dotenv()   # Load .env values properly


app = FastAPI(title="Shamor Ride API")


# -------------------------------------------------------------------
# ✔ FIXED CORS — NO MIXING "*" WITH SPECIFIC DOMAINS
# -------------------------------------------------------------------
# "*" breaks cookies / auth headers on browsers and can cause 401 issues.

origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "http://localhost:5500",            # for local testing
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,          # needed for Authorization header
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# ✔ TABLE CREATION (SAFE FOR RENDER)
# -------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


# -------------------------------------------------------------------
# ✔ ROUTERS (NO DUPLICATE PREFIXES)
# -------------------------------------------------------------------
app.include_router(auth_router)     # /auth
app.include_router(rides_router)    # /rides
app.include_router(wallet_router)   # /wallet
app.include_router(admin_router)    # /admin
app.include_router(ws_router)       # /ws


# -------------------------------------------------------------------
# ✔ ROOT ENDPOINT
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running with PostgreSQL"}
