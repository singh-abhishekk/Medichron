"""
Main FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
static_path = Path("static")
static_path.mkdir(exist_ok=True)

qr_code_path = Path(settings.QR_CODE_DIR)
qr_code_path.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Add url_for function to templates for Flask compatibility
def url_for(endpoint: str, **values):
    """Mimic Flask's url_for for template compatibility."""
    if endpoint == "static":
        filename = values.get("filename", "")
        return f"/static/{filename}"
    return f"/{endpoint}"

templates.env.globals["url_for"] = url_for


@app.get("/")
def root():
    """
    Root endpoint with API information.

    Returns:
        API information and documentation links
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


# Template routes for frontend pages
@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    """Serve the home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/doctor-register", response_class=HTMLResponse)
async def doctor_register_page(request: Request):
    """Serve the doctor registration page."""
    return templates.TemplateResponse("doctor.html", {"request": request})


@app.get("/dashboard/user", response_class=HTMLResponse)
async def user_dashboard_page(request: Request):
    """Serve the user dashboard page."""
    return templates.TemplateResponse("dashboardUser.html", {"request": request})


@app.get("/dashboard/doctor", response_class=HTMLResponse)
async def doctor_dashboard_page(request: Request):
    """Serve the doctor dashboard page."""
    return templates.TemplateResponse("dashboardDoc.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Serve the contact page."""
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/history/user", response_class=HTMLResponse)
async def user_history_page(request: Request):
    """Serve the user history page."""
    return templates.TemplateResponse("historyUser.html", {"request": request})


@app.get("/history/doctor", response_class=HTMLResponse)
async def doctor_history_page(request: Request):
    """Serve the doctor history page."""
    return templates.TemplateResponse("historyDoctor.html", {"request": request})


@app.get("/qr-generate", response_class=HTMLResponse)
async def qr_generate_page(request: Request):
    """Serve the QR code generation page."""
    return templates.TemplateResponse("qrgenerate.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
