# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from auth import router as auth_router
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router
from realtime import router as ws_router  # your websocket routes

app = FastAPI(title="Shamor Ride API")

origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "*",  # keep for now so local testing works
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

# Routers (each already has its own prefix)
app.include_router(auth_router)
app.include_router(rides_router)
app.include_router(wallet_router)
app.include_router(admin_router)
app.include_router(ws_router)


@app.get("/")
def root():
    return {"status": "Shamor-Ride backend running with PostgreSQL"}


