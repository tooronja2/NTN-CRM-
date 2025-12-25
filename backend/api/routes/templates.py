"""
Rutas API para Plantillas
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header

from ..models.schemas import Plantilla, PlantillaCreate, PlantillaUpdate
from ..services.database import (
    create_plantilla, get_plantillas, get_plantilla,
    update_plantilla, delete_plantilla
)
from ..services.email_service import render_template

router = APIRouter(prefix="/plantillas", tags=["Plantillas"])


@router.get("/", response_model=List[Plantilla])
async def listar_plantillas(
    x_telegram_id: int = Header(...),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: email, telegram")
):
    """Lista todas las plantillas del usuario."""
    return get_plantillas(x_telegram_id, tipo)


@router.post("/", response_model=Plantilla)
async def crear_plantilla(
    data: PlantillaCreate,
    x_telegram_id: int = Header(...)
):
    """Crea una nueva plantilla."""
    if data.tipo not in ["email", "telegram"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'email' o 'telegram'")
    
    result = create_plantilla(x_telegram_id, data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Error creando plantilla")
    return result


@router.get("/variables")
async def obtener_variables_disponibles():
    """
    Devuelve las variables disponibles para usar en plantillas.
    """
    return {
        "variables": [
            {"nombre": "titulo", "descripcion": "Título de la tarea"},
            {"nombre": "descripcion", "descripcion": "Descripción de la tarea"},
            {"nombre": "fecha_vencimiento", "descripcion": "Fecha de vencimiento"},
            {"nombre": "prioridad", "descripcion": "Prioridad de la tarea"},
            {"nombre": "estado", "descripcion": "Estado actual de la tarea"},
            {"nombre": "contacto_nombre", "descripcion": "Nombre del contacto"},
            {"nombre": "contacto_email", "descripcion": "Email del contacto"},
            {"nombre": "contacto_empresa", "descripcion": "Empresa del contacto"},
            {"nombre": "proyecto_nombre", "descripcion": "Nombre del proyecto"},
        ],
        "ejemplo": "Hola {{contacto_nombre}}, te recuerdo sobre {{titulo}}."
    }


@router.get("/{plantilla_id}", response_model=Plantilla)
async def obtener_plantilla(
    plantilla_id: int,
    x_telegram_id: int = Header(...)
):
    """Obtiene una plantilla por ID."""
    result = get_plantilla(plantilla_id, x_telegram_id)
    if not result:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return result


@router.put("/{plantilla_id}", response_model=Plantilla)
async def actualizar_plantilla(
    plantilla_id: int,
    data: PlantillaUpdate,
    x_telegram_id: int = Header(...)
):
    """Actualiza una plantilla."""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    if "tipo" in update_data and update_data["tipo"] not in ["email", "telegram"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'email' o 'telegram'")
    
    result = update_plantilla(plantilla_id, x_telegram_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return result


@router.delete("/{plantilla_id}")
async def eliminar_plantilla(
    plantilla_id: int,
    x_telegram_id: int = Header(...)
):
    """Elimina una plantilla."""
    success = delete_plantilla(plantilla_id, x_telegram_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return {"success": True, "message": "Plantilla eliminada"}


@router.post("/{plantilla_id}/preview")
async def preview_plantilla(
    plantilla_id: int,
    x_telegram_id: int = Header(...),
    variables: dict = None
):
    """
    Genera un preview de la plantilla con variables de ejemplo.
    """
    plantilla = get_plantilla(plantilla_id, x_telegram_id)
    if not plantilla:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    # Variables de ejemplo si no se proporcionan
    if not variables:
        variables = {
            "titulo": "Reunión con Cliente",
            "descripcion": "Discutir propuesta del proyecto",
            "fecha_vencimiento": "2024-01-15",
            "prioridad": "alta",
            "estado": "pendiente",
            "contacto_nombre": "Juan Pérez",
            "contacto_email": "juan@ejemplo.com",
            "contacto_empresa": "ABC Corp",
            "proyecto_nombre": "Proyecto Demo"
        }
    
    preview = {
        "mensaje": render_template(plantilla["mensaje"], variables)
    }
    
    if plantilla.get("asunto"):
        preview["asunto"] = render_template(plantilla["asunto"], variables)
    
    return preview
