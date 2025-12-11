# main.py
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

# Load .env BEFORE importing modules that read env vars (like auth.py)
load_dotenv()

# Routers
from auth import router as auth_router
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router
from realtime import router as ws_router


app = FastAPI(title="Shamor Ride API")


# CORS origins: keep frontend domains + "*" for now
origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "*",
]


@app.on_event("startup")
def on_startup():
    """
    Create tables on startup. With SQLAlchemy this is safe to call; it
    will only create missing tables.
    """
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # you can tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# IMPORTANT: routers ALREADY have prefixes defined in each file
# auth.py      -> prefix="/auth"
# rides.py     -> prefix="/rides"
# wallet.py    -> prefix="/wallet"
# admin.py     -> prefix="/admin"
# realtime.py  -> websocket routes under /ws/...
app.include_router(auth_router)
app.include_router(rides_router)
app.include_router(wallet_router)
app.include_router(admin_router)
app.include_router(ws_router)


@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running with PostgreSQL"}


# Optional: simple health endpoint for Render / monitoring
@app.get("/health")
def health():
    return {"ok": True}
