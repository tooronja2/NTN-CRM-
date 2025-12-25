"""
Rutas API para Contactos
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header

from ..models.schemas import (
    Contacto, ContactoCreate, ContactoUpdate, APIResponse
)
from ..services.database import (
    create_contacto, get_contactos, get_contacto,
    update_contacto, delete_contacto, get_historial_contacto
)

router = APIRouter(prefix="/contactos", tags=["Contactos"])


def get_user_id(x_telegram_id: int = Header(...)) -> int:
    """Obtiene el ID del usuario autenticado desde header."""
    return x_telegram_id


@router.get("/", response_model=List[Contacto])
async def listar_contactos(
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    x_telegram_id: int = Header(...)
):
    """Lista todos los contactos del usuario."""
    return get_contactos(x_telegram_id, search)


@router.post("/", response_model=Contacto)
async def crear_contacto(
    data: ContactoCreate,
    x_telegram_id: int = Header(...)
):
    """Crea un nuevo contacto."""
    result = create_contacto(x_telegram_id, data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Error creando contacto")
    return result


@router.get("/{contacto_id}", response_model=Contacto)
async def obtener_contacto(
    contacto_id: int,
    x_telegram_id: int = Header(...)
):
    """Obtiene un contacto por ID."""
    result = get_contacto(contacto_id, x_telegram_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return result


@router.put("/{contacto_id}", response_model=Contacto)
async def actualizar_contacto(
    contacto_id: int,
    data: ContactoUpdate,
    x_telegram_id: int = Header(...)
):
    """Actualiza un contacto."""
    # Filtrar campos None
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    result = update_contacto(contacto_id, x_telegram_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return result


@router.delete("/{contacto_id}")
async def eliminar_contacto(
    contacto_id: int,
    x_telegram_id: int = Header(...)
):
    """Elimina un contacto."""
    success = delete_contacto(contacto_id, x_telegram_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return {"success": True, "message": "Contacto eliminado"}


@router.get("/{contacto_id}/historial")
async def obtener_historial(
    contacto_id: int,
    x_telegram_id: int = Header(...),
    limit: int = Query(20, le=100)
):
    """Obtiene el historial de interacciones con un contacto."""
    # Verificar que el contacto existe y es del usuario
    contacto = get_contacto(contacto_id, x_telegram_id)
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    return get_historial_contacto(contacto_id, limit)
