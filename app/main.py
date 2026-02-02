import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.chain import run_food_query
from app.data import df  # Import df to check if it loads

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Food Suitability Search API",
    version="1.0.0"
)
ENV = os.getenv("ENV", "local")

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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# Add a debug endpoint to check dataframe (REMOVE IN PRODUCTION)
@app.get("/api/debug/df")
def check_dataframe():
    # ⚠️ TODO: Add authentication/remove in production
    try:
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "sample_count": min(2, len(df))  # Don't expose actual data
        }
    except Exception as e:
        return {"error": "Dataframe not available"}

class SearchRequest(BaseModel):
    query: str


@app.post("/api/search")
def search_food(req: SearchRequest):
    try:
        print(f"Received query: {req.query}")  # Debug logging
        result = run_food_query(req.query)
        print(f"Query result: {result}")  # Debug logging
        return result
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug logging
        print(f"Error type: {type(e).__name__}")  # Debug logging
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.get("/api/health")
def health():
    return {"status": "ok"}
