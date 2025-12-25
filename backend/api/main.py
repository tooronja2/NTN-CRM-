"""
CRM Follow-Up Automation - FastAPI Backend
==========================================
API principal del CRM
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routes import contacts, tasks, projects, templates
from .services.database import get_or_create_usuario, get_usuario, update_usuario, get_dashboard_stats
from .services.email_service import test_smtp_connection, get_smtp_status
from .services.scheduler import start_scheduler, stop_scheduler, trigger_manual_check
from .models.schemas import UsuarioCreate, UsuarioUpdate, DashboardStats

load_dotenv()

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: startup y shutdown."""
    # Startup
    logger.info("🚀 Iniciando CRM API...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("👋 Cerrando CRM API...")
    stop_scheduler()


# App
app = FastAPI(
    title="CRM Follow-Up Automation",
    description="API para gestión de contactos, tareas y automatización de follow-ups",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(contacts.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(templates.router, prefix="/api")


# --- RUTAS PRINCIPALES ---

@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "ok",
        "service": "CRM Follow-Up Automation",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health():
    """Health check detallado."""
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running"
    }


# --- USUARIOS ---

@app.post("/api/usuarios/register")
async def registrar_usuario(data: UsuarioCreate):
    """
    Registra o actualiza un usuario.
    Se llama desde el bot de Telegram al hacer /start.
    """
    usuario = get_or_create_usuario(
        telegram_id=data.telegram_id,
        nombre=data.nombre,
        email=data.email
    )
    return usuario


@app.get("/api/usuarios/me")
async def obtener_mi_perfil(x_telegram_id: int = Header(...)):
    """Obtiene el perfil del usuario actual."""
    usuario = get_usuario(x_telegram_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.put("/api/usuarios/me")
async def actualizar_mi_perfil(
    data: UsuarioUpdate,
    x_telegram_id: int = Header(...)
):
    """Actualiza el perfil del usuario actual."""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    usuario = update_usuario(x_telegram_id, update_data)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.get("/api/smtp/status")
async def smtp_status():
    """
    Obtiene el estado de configuración SMTP del servidor.
    Útil para verificar que el email centralizado está configurado.
    """
    return get_smtp_status()


@app.post("/api/smtp/test")
async def smtp_test():
    """
    Prueba la conexión SMTP del servidor.
    """
    result = test_smtp_connection()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


# --- DASHBOARD ---

@app.get("/api/dashboard", response_model=DashboardStats)
async def obtener_dashboard(x_telegram_id: int = Header(...)):
    """Obtiene estadísticas para el dashboard."""
    return get_dashboard_stats(x_telegram_id)


# --- UTILIDADES ---

@app.post("/api/trigger-reminders")
async def trigger_reminders(x_telegram_id: int = Header(...)):
    """
    Dispara manualmente la verificación de recordatorios.
    Útil para testing.
    """
    result = await trigger_manual_check()
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
