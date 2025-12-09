from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from auth import router as auth_router, get_current_user
from rides import router as rides_router
from wallet import router as wallet_router
from admin import router as admin_router

app = FastAPI(title="Shamor Ride API")

origins = [
    "https://starmo-ride-frontend.onrender.com",
    "https://starmo-ride-frontend.render.com",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
def startup():
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


app.include_router(auth_router)
app.include_router(rides_router)
app.include_router(wallet_router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {"status": "Shamor Ride API running PostgreSQL OK"}
