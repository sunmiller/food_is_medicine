import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Load env vars FIRST, before importing modules that need them
load_dotenv()

# NOW import modules that depend on environment variables
# from app.services.query_service import query_service
from app.routers.food import router as food_router

ENV = os.getenv("ENV", "local")

app = FastAPI(
    title="Food Suitability Search API",
    version="1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY") or os.getenv("SESSION_SECRET") or "dev-insecure-session-key",
    https_only=ENV == "prod",
    same_site="lax"
)

# ---------- dbtest ----------
# Test saving a query
# user_id = query_service.get_or_create_anonymous_user()
# print(f"Created test user with ID: {user_id}")
        
        
# ---------- CORS ----------

if ENV == "prod":
    origins = ["https://eatforhealing.com","https://www.eatforhealing.com"]
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
