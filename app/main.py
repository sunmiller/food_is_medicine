import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers.food import router as food_router

# Load env vars
load_dotenv()

ENV = os.getenv("ENV", "local")

app = FastAPI(
    title="Food Suitability Search API",
    version="1.0.0"
)

# ---------- CORS ----------

if ENV == "prod":
    origins = ["https://app.example.com"]
else:
    origins = ["http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- STATIC FILES ----------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# ---------- ROUTERS ----------

app.include_router(food_router)
