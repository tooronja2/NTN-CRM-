"""
Rutas API para Tareas
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Header

from ..models.schemas import (
    Tarea, TareaCreate, TareaUpdate,
    RecordatorioConfig, RecordatorioConfigCreate
)
from ..services.database import (
    create_tarea, get_tareas, get_tarea, get_tareas_pendientes_hoy,
    update_tarea, delete_tarea, cambiar_estado_tarea,
    get_recordatorios_config, create_recordatorio_config, delete_recordatorio_config
)

router = APIRouter(prefix="/tareas", tags=["Tareas"])


@router.get("/", response_model=List[Tarea])
async def listar_tareas(
    x_telegram_id: int = Header(...),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    contacto_id: Optional[int] = Query(None, description="Filtrar por contacto"),
    proyecto_id: Optional[int] = Query(None, description="Filtrar por proyecto"),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None)
):
    """Lista tareas con filtros opcionales."""
    return get_tareas(
        x_telegram_id,
        estado=estado,
        contacto_id=contacto_id,
        proyecto_id=proyecto_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )


@router.get("/hoy", response_model=List[Tarea])
async def listar_tareas_hoy(x_telegram_id: int = Header(...)):
    """Lista tareas pendientes para hoy."""
    return get_tareas_pendientes_hoy(x_telegram_id)


@router.get("/kanban")
async def obtener_kanban(x_telegram_id: int = Header(...)):
    """
    Obtiene tareas organizadas para vista Kanban.
    """
    tareas = get_tareas(x_telegram_id)
    
    kanban = {
        "pendiente": [],
        "en_seguimiento": [],
        "esperando_respuesta": [],
        "completado": []
    }
    
    for tarea in tareas:
        estado = tarea.get("estado", "pendiente")
        if estado in kanban:
            kanban[estado].append(tarea)
    
    return kanban


@router.post("/", response_model=Tarea)
async def crear_tarea(
    data: TareaCreate,
    x_telegram_id: int = Header(...)
):
    """Crea una nueva tarea con recordatorios opcionales."""
    # Extraer recordatorios si existen
    recordatorios = None
    tarea_data = data.model_dump()
    
    if "recordatorios" in tarea_data:
        recordatorios_raw = tarea_data.pop("recordatorios")
        if recordatorios_raw:
            recordatorios = []
            for rec in recordatorios_raw:
                # Convertir time a string si es necesario
                if hasattr(rec.get("hora"), "isoformat"):
                    rec["hora"] = rec["hora"].isoformat()
                recordatorios.append(rec)
    
    result = create_tarea(x_telegram_id, tarea_data, recordatorios)
    if not result:
        raise HTTPException(status_code=500, detail="Error creando tarea")
    return result


@router.get("/{tarea_id}", response_model=Tarea)
async def obtener_tarea(
    tarea_id: int,
    x_telegram_id: int = Header(...)
):
    """Obtiene una tarea por ID."""
    result = get_tarea(tarea_id, x_telegram_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return result


@router.put("/{tarea_id}", response_model=Tarea)
async def actualizar_tarea(
    tarea_id: int,
    data: TareaUpdate,
    x_telegram_id: int = Header(...)
):
    """Actualiza una tarea."""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    result = update_tarea(tarea_id, x_telegram_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return result


@router.patch("/{tarea_id}/estado")
async def cambiar_estado(
    tarea_id: int,
    estado: str = Query(..., description="Nuevo estado"),
    x_telegram_id: int = Header(...)
):
    """Cambia el estado de una tarea (útil para Kanban drag & drop)."""
    estados_validos = ["pendiente", "en_seguimiento", "esperando_respuesta", "completado"]
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Usar: {estados_validos}")
    
    result = cambiar_estado_tarea(tarea_id, x_telegram_id, estado)
    if not result:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return result


@router.delete("/{tarea_id}")
async def eliminar_tarea(
    tarea_id: int,
    x_telegram_id: int = Header(...)
):
    """Elimina una tarea."""
    success = delete_tarea(tarea_id, x_telegram_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"success": True, "message": "Tarea eliminada"}


# --- RECORDATORIOS CONFIG ---

@router.get("/{tarea_id}/recordatorios", response_model=List[RecordatorioConfig])
async def listar_recordatorios(
    tarea_id: int,
    x_telegram_id: int = Header(...)
):
    """Lista recordatorios configurados de una tarea."""
    # Verificar que la tarea existe y es del usuario
    tarea = get_tarea(tarea_id, x_telegram_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return get_recordatorios_config(tarea_id)


@router.post("/{tarea_id}/recordatorios", response_model=RecordatorioConfig)
async def agregar_recordatorio(
    tarea_id: int,
    data: RecordatorioConfigCreate,
    x_telegram_id: int = Header(...)
):
    """Agrega un recordatorio a una tarea."""
    # Verificar que la tarea existe y es del usuario
    tarea = get_tarea(tarea_id, x_telegram_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    rec_data = data.model_dump()
    if hasattr(rec_data.get("hora"), "isoformat"):
        rec_data["hora"] = rec_data["hora"].isoformat()
    
    result = create_recordatorio_config(tarea_id, rec_data)
    if not result:
        raise HTTPException(status_code=500, detail="Error creando recordatorio")
    return result


@router.delete("/{tarea_id}/recordatorios/{recordatorio_id}")
async def eliminar_recordatorio(
    tarea_id: int,
    recordatorio_id: int,
    x_telegram_id: int = Header(...)
):
    """Elimina un recordatorio de una tarea."""
    # Verificar que la tarea existe y es del usuario
    tarea = get_tarea(tarea_id, x_telegram_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    success = delete_recordatorio_config(recordatorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    return {"success": True, "message": "Recordatorio eliminado"}
