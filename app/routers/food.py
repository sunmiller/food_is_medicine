from pathlib import Path
import os
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth, OAuthError
from pydantic import BaseModel

from app.chain import run_food_query
from app.data import df
from app.services.email_service import send_contact_email, EmailNotConfiguredError

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SITEMAP_PATH = PROJECT_ROOT / "sitemap.xml"
ROBOTS_PATH = PROJECT_ROOT / "robots.txt"

templates = Jinja2Templates(directory="templates")

oauth = OAuth()
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
public_base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

if google_client_id and google_client_secret:
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=google_client_id,
        client_secret=google_client_secret,
        client_kwargs={"scope": "openid email profile"},
    )


def render_page(request: Request, name: str, context: dict | None = None):
    merged_context = {
        "user_session": request.session.get("user") if request.session else None,
        "current_path": request.url.path,
    }
    if context:
        merged_context.update(context)

    return templates.TemplateResponse(
        request=request,
        name=name,
        context=merged_context,
    )


def get_google_callback_url(request: Request) -> str:
    if public_base_url:
        return f"{public_base_url}{request.app.url_path_for('auth_google_callback')}"

    return str(request.url_for("auth_google_callback"))


# ---------- MODELS ----------

class SearchRequest(BaseModel):
    query: str


# ---------- HTML ROUTES ----------

@router.get("/sitemap.xml", response_class=FileResponse)
def sitemap():
    return FileResponse(str(SITEMAP_PATH), media_type="application/xml")


@router.get("/robots.txt", response_class=FileResponse)
def robots():
    return FileResponse(str(ROBOTS_PATH), media_type="text/plain")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_page(
        request=request,
        name="index.html",
        context={
            "api_base": "/api",
        }
    )
@router.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return render_page(
        request=request,
        name="about.html",
        context={}
    )

@router.get("/foodfordiabetes", response_class=HTMLResponse)
def food_for_diabetes(request: Request):
    return render_page(
        request=request,
        name="foodfordiabetes.html",
        context={}
    )

@router.get("/diabetescondition", response_class=HTMLResponse)
def diabetes_condition(request: Request):
    return render_page(
        request=request,
        name="diabetescondition.html",
        context={}
    )


@router.get("/blog", response_class=HTMLResponse)
def diabetes_condition(request: Request):
    return render_page(
        request=request,
        name="blog.html",
        context={}
    )
@router.get("/events", response_class=HTMLResponse)
def diabetes_condition(request: Request):
    return render_page(
        request=request,
        name="events.html",
        context={}
    )
@router.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return render_page(
        request=request,
        name="contact.html",
        context={}
    )

@router.post("/contact", response_class=HTMLResponse)
async def contact_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form("")
):
    try:
        await send_contact_email(name=name, email=email, message=message)
        status = "sent"
    except EmailNotConfiguredError:
        status = "not_configured"
    except Exception:
        status = "error"

    return render_page(
        request=request,
        name="contact.html",
        context={"contact_status": status}
    )

@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return render_page(
        request=request,
        name="login.html",
        context={
            "google_login_url": request.app.url_path_for("auth_google_login"),
            "google_auth_enabled": bool(google_client_id and google_client_secret),
            "google_error": request.query_params.get("error")
        }
    )

@router.get("/auth/google/login")
async def auth_google_login(request: Request):
    if not (google_client_id and google_client_secret):
        return RedirectResponse(url="/login?error=google_not_configured", status_code=302)

    redirect_uri = get_google_callback_url(request)
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    if not (google_client_id and google_client_secret):
        return RedirectResponse(url="/login?error=google_not_configured", status_code=302)

    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            user_info = await oauth.google.parse_id_token(request, token)

        if not user_info:
            return RedirectResponse(url="/login?error=google_auth_failed", status_code=302)

        request.session["user"] = {
            "sub": user_info.get("sub"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
        }
        return RedirectResponse(url="/", status_code=302)
    except OAuthError:
        return RedirectResponse(url="/login?error=google_auth_failed", status_code=302)


@router.get("/logout")
def logout(request: Request):
    if request.session:
        request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=302)

@router.get("/test", response_class=HTMLResponse)
def test_page(request: Request):
    user_session = request.session.get("user") if request.session else None
    user_email = user_session.get("email") if user_session else None

    return render_page(
        request=request,
        name="test.html",
        context={
            "user_email": user_email,
            "user_session": user_session,
            "session_data": dict(request.session)
        }
    )


@router.post("/search", response_class=HTMLResponse)
async def search_food_form(
    request: Request,
    query: str = Form(...)
):
    data = run_food_query(query)

    return render_page(
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
