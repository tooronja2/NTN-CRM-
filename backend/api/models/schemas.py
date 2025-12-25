"""
Modelos Pydantic para el CRM
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# =============================================
# USUARIOS
# =============================================
class UsuarioBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    timezone: str = "America/Argentina/Buenos_Aires"

class UsuarioCreate(UsuarioBase):
    telegram_id: int

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None  # Email del usuario para Reply-To en recordatorios
    timezone: Optional[str] = None

class Usuario(UsuarioBase):
    telegram_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================
# CONTACTOS
# =============================================
class ContactoBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    telegram_id: Optional[int] = None
    empresa: Optional[str] = None
    notas: Optional[str] = None

class ContactoCreate(ContactoBase):
    pass

class ContactoUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    telegram_id: Optional[int] = None
    empresa: Optional[str] = None
    notas: Optional[str] = None

class Contacto(ContactoBase):
    id: int
    usuario_telegram_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================
# PROYECTOS
# =============================================
class ProyectoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    contacto_id: Optional[int] = None
    estado: str = "activo"

class ProyectoCreate(ProyectoBase):
    pass

class ProyectoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    contacto_id: Optional[int] = None
    estado: Optional[str] = None

class Proyecto(ProyectoBase):
    id: int
    usuario_telegram_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================
# TAREAS
# =============================================
class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    contacto_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    fecha_vencimiento: Optional[datetime] = None
    estado: str = "pendiente"
    prioridad: str = "media"
    frecuencia_repeticion: Optional[str] = None
    canal_notificacion: str = "telegram"
    plantilla_id: Optional[int] = None

class TareaCreate(TareaBase):
    # Recordatorios opcionales al crear
    recordatorios: Optional[List["RecordatorioConfigCreate"]] = None

class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    contacto_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    fecha_vencimiento: Optional[datetime] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    frecuencia_repeticion: Optional[str] = None
    canal_notificacion: Optional[str] = None
    plantilla_id: Optional[int] = None

class Tarea(TareaBase):
    id: int
    usuario_telegram_id: int
    created_at: datetime
    updated_at: datetime
    # Relaciones opcionales
    contacto: Optional[Contacto] = None
    proyecto: Optional[Proyecto] = None

    class Config:
        from_attributes = True


# =============================================
# RECORDATORIOS CONFIG
# =============================================
class RecordatorioConfigBase(BaseModel):
    dias_antes: int = 0
    hora: time = time(9, 0)
    canal: str = "telegram"
    activo: bool = True

class RecordatorioConfigCreate(RecordatorioConfigBase):
    tarea_id: Optional[int] = None  # Se asigna al crear tarea

class RecordatorioConfigUpdate(BaseModel):
    dias_antes: Optional[int] = None
    hora: Optional[time] = None
    canal: Optional[str] = None
    activo: Optional[bool] = None

class RecordatorioConfig(RecordatorioConfigBase):
    id: int
    tarea_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================
# RECORDATORIOS ENVIADOS (LOG)
# =============================================
class RecordatorioEnviadoBase(BaseModel):
    tarea_id: Optional[int] = None
    recordatorio_config_id: Optional[int] = None
    canal: str
    estado: str = "enviado"
    mensaje: Optional[str] = None
    error_mensaje: Optional[str] = None

class RecordatorioEnviadoCreate(RecordatorioEnviadoBase):
    pass

class RecordatorioEnviado(RecordatorioEnviadoBase):
    id: int
    fecha_envio: datetime

    class Config:
        from_attributes = True


# =============================================
# PLANTILLAS
# =============================================
class PlantillaBase(BaseModel):
    nombre: str
    tipo: str  # 'email', 'telegram'
    asunto: Optional[str] = None  # Solo para email
    mensaje: str
    es_default: bool = False

class PlantillaCreate(PlantillaBase):
    pass

class PlantillaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    asunto: Optional[str] = None
    mensaje: Optional[str] = None
    es_default: Optional[bool] = None

class Plantilla(PlantillaBase):
    id: int
    usuario_telegram_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================
# HISTORIAL
# =============================================
class HistorialInteraccion(BaseModel):
    id: int
    usuario_telegram_id: int
    contacto_id: Optional[int]
    tarea_id: Optional[int]
    tipo: str
    descripcion: Optional[str]
    metadata: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================
# RESPUESTAS API
# =============================================
class DashboardStats(BaseModel):
    total_contactos: int
    total_tareas_pendientes: int
    total_tareas_hoy: int
    total_proyectos_activos: int
    tareas_por_estado: dict
    proximos_vencimientos: List[Tarea]


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
