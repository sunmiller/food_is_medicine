import os
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.chain import run_food_query
from app.data import df
from app.services.query_service import QueryPersistenceService

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ---------- MODELS ----------

class SearchRequest(BaseModel):
    query: str


# ---------- HTML ROUTES ----------

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "api_base": "/api"
        }
    )
@router.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={}
    )

@router.get("/foodfordiabetes", response_class=HTMLResponse)
def food_for_diabetes(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="foodfordiabetes.html",
        context={}
    )

@router.get("/diabetescondition", response_class=HTMLResponse)
def diabetes_condition(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="diabetescondition.html",
        context={}
    )

@router.get("/test", response_class=HTMLResponse)
def test_page(request: Request):
    # Lazy load the query service to avoid env var loading issues
    query_service = QueryPersistenceService()

    user_id = query_service.get_or_create_anonymous_user()

    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={
            "user_id": user_id
        }
    )


@router.post("/search", response_class=HTMLResponse)
async def search_food_form(
    request: Request,
    query: str = Form(...)
):
    data = run_food_query(query)

    return templates.TemplateResponse(
        request=request,
        name="partials/results.html",
        context={
            "results": data.get("results", [])
        }
    )

# ---------- API ROUTES ----------

@router.post("/api/search")
def search_food_api(req: SearchRequest):
    try:
        result = run_food_query(req.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )


@router.get("/api/health")
def health():
    return {"status": "ok"}


# ⚠️ REMOVE OR PROTECT IN PROD
@router.get("/api/debug/df")
def check_dataframe():
    try:
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "sample_count": min(2, len(df))
        }
    except Exception:
        return {"error": "Dataframe not available"}
