# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import engine
from auth import router as auth_router
from realtime import router as realtime_router
from surge import router as surge_router
from admin import router as admin_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shamor Ride API",
    version="1.0.0"
)

# ------------------------------
# CORS SETTINGS
# ------------------------------
origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://shamor-ride-frontend.onrender.com",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# ROUTERS
# ------------------------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(realtime_router, prefix="/ws", tags=["WebSockets"])
app.include_router(surge_router, prefix="/admin", tags=["Surge"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

@app.get("/")
def root():
    return {"message": "Shamor Ride API is running!"}
