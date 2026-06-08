"""
Aplicación principal FastAPI - IP Manager.
Gestión completa de direcciones IPv4 e IPv6.
Compatible con Python 3.12 y Docker.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from app.routers import (
    ipv4_router,
    ipv6_router,
    conversion_router,
    history_router,
    export_router,
    local_router,
)

# ─────────────────────────────────────────────
#  Instancia FastAPI
# ─────────────────────────────────────────────
app = FastAPI(
    title="IP Manager",
    description=(
        "Aplicación completa para gestión de direcciones IPv4 e IPv6. "
        "Incluye cálculo de subredes, conversión, detección de interfaces "
        "y clasificación automática de IPs."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Proyecto Final - Redes",
        "email": "admin@ipmanager.local",
    },
    license_info={
        "name": "MIT",
    },
)

# ─────────────────────────────────────────────
#  CORS
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Archivos estáticos y templates
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ─────────────────────────────────────────────
#  Incluir routers
# ─────────────────────────────────────────────
app.include_router(ipv4_router.router)
app.include_router(ipv6_router.router)
app.include_router(conversion_router.router)
app.include_router(history_router.router)
app.include_router(export_router.router)
app.include_router(local_router.router)


# ─────────────────────────────────────────────
#  Rutas de la interfaz web
# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """Página principal de la aplicación."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Sistema"], summary="Health check")
async def health():
    """Verifica que la aplicación está operativa."""
    return {"status": "ok", "version": "1.0.0", "app": "IP Manager"}
