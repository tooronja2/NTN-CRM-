"""
Rutas API para Proyectos
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header

from ..models.schemas import Proyecto, ProyectoCreate, ProyectoUpdate
from ..services.database import (
    create_proyecto, get_proyectos, get_proyecto,
    update_proyecto, delete_proyecto, get_tareas
)

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])


@router.get("/", response_model=List[Proyecto])
async def listar_proyectos(
    x_telegram_id: int = Header(...),
    estado: Optional[str] = Query(None, description="Filtrar por estado")
):
    """Lista todos los proyectos del usuario."""
    return get_proyectos(x_telegram_id, estado)


@router.post("/", response_model=Proyecto)
async def crear_proyecto(
    data: ProyectoCreate,
    x_telegram_id: int = Header(...)
):
    """Crea un nuevo proyecto."""
    result = create_proyecto(x_telegram_id, data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Error creando proyecto")
    return result


@router.get("/{proyecto_id}", response_model=Proyecto)
async def obtener_proyecto(
    proyecto_id: int,
    x_telegram_id: int = Header(...)
):
    """Obtiene un proyecto por ID."""
    result = get_proyecto(proyecto_id, x_telegram_id)
    if not result:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return result


@router.put("/{proyecto_id}", response_model=Proyecto)
async def actualizar_proyecto(
    proyecto_id: int,
    data: ProyectoUpdate,
    x_telegram_id: int = Header(...)
):
    """Actualiza un proyecto."""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    result = update_proyecto(proyecto_id, x_telegram_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return result


@router.delete("/{proyecto_id}")
async def eliminar_proyecto(
    proyecto_id: int,
    x_telegram_id: int = Header(...)
):
    """Elimina un proyecto."""
    success = delete_proyecto(proyecto_id, x_telegram_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"success": True, "message": "Proyecto eliminado"}


@router.get("/{proyecto_id}/tareas")
async def listar_tareas_proyecto(
    proyecto_id: int,
    x_telegram_id: int = Header(...)
):
    """Lista todas las tareas de un proyecto."""
    # Verificar que el proyecto existe
    proyecto = get_proyecto(proyecto_id, x_telegram_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    return get_tareas(x_telegram_id, proyecto_id=proyecto_id)
