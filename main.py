# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from auth import router as auth_router
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router
from realtime import router as ws_router

app = FastAPI(title="Shamor Ride API")

origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "*",
]

@app.on_event("startup")
def on_startup():
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✔ ROUTERS LOADED WITH PROPER PREFIXES
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rides_router, prefix="/rides", tags=["Rides"])
app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(ws_router)  # websocket has its own paths

@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running with PostgreSQL"}
