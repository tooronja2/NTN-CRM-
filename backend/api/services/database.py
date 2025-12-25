"""
Servicio de Base de Datos - Conexión a Supabase
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta

from dotenv import load_dotenv
from supabase import create_client, Client
import pytz

load_dotenv()

logger = logging.getLogger(__name__)

# Configuración
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TIMEZONE = os.getenv("TIMEZONE", "America/Argentina/Buenos_Aires")

TZ = pytz.timezone(TIMEZONE)

# Cliente Supabase
_supabase: Optional[Client] = None

def get_supabase() -> Client:
    """Obtiene el cliente de Supabase (singleton)."""
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridos")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Conectado a Supabase")
    return _supabase


# =============================================
# USUARIOS
# =============================================
def get_or_create_usuario(telegram_id: int, nombre: str, email: str = None) -> Dict:
    """Obtiene o crea un usuario por su telegram_id."""
    db = get_supabase()
    
    # Buscar existente
    resp = db.table("usuarios").select("*").eq("telegram_id", telegram_id).execute()
    
    if resp.data:
        return resp.data[0]
    
    # Crear nuevo
    new_user = {
        "telegram_id": telegram_id,
        "nombre": nombre,
        "email": email,
        "timezone": TIMEZONE
    }
    resp = db.table("usuarios").insert(new_user).execute()
    
    if resp.data:
        # Crear plantillas por defecto
        create_default_plantillas(telegram_id)
        return resp.data[0]
    
    raise Exception("Error creando usuario")


def update_usuario(telegram_id: int, data: Dict) -> Dict:
    """Actualiza datos de usuario."""
    db = get_supabase()
    resp = db.table("usuarios").update(data).eq("telegram_id", telegram_id).execute()
    return resp.data[0] if resp.data else None


def get_usuario(telegram_id: int) -> Optional[Dict]:
    """Obtiene un usuario por telegram_id."""
    db = get_supabase()
    resp = db.table("usuarios").select("*").eq("telegram_id", telegram_id).execute()
    return resp.data[0] if resp.data else None


# =============================================
# CONTACTOS
# =============================================
def create_contacto(usuario_telegram_id: int, data: Dict) -> Dict:
    """Crea un nuevo contacto."""
    db = get_supabase()
    data["usuario_telegram_id"] = usuario_telegram_id
    resp = db.table("contactos").insert(data).execute()
    return resp.data[0] if resp.data else None


def get_contactos(usuario_telegram_id: int, search: str = None) -> List[Dict]:
    """Lista contactos de un usuario."""
    db = get_supabase()
    query = db.table("contactos").select("*").eq("usuario_telegram_id", usuario_telegram_id)
    
    if search:
        query = query.ilike("nombre", f"%{search}%")
    
    resp = query.order("nombre").execute()
    return resp.data or []


def get_contacto(contacto_id: int, usuario_telegram_id: int) -> Optional[Dict]:
    """Obtiene un contacto por ID."""
    db = get_supabase()
    resp = db.table("contactos").select("*")\
        .eq("id", contacto_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def update_contacto(contacto_id: int, usuario_telegram_id: int, data: Dict) -> Optional[Dict]:
    """Actualiza un contacto."""
    db = get_supabase()
    resp = db.table("contactos").update(data)\
        .eq("id", contacto_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def delete_contacto(contacto_id: int, usuario_telegram_id: int) -> bool:
    """Elimina un contacto."""
    db = get_supabase()
    resp = db.table("contactos").delete()\
        .eq("id", contacto_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return len(resp.data) > 0 if resp.data else False


# =============================================
# PROYECTOS
# =============================================
def create_proyecto(usuario_telegram_id: int, data: Dict) -> Dict:
    """Crea un nuevo proyecto."""
    db = get_supabase()
    data["usuario_telegram_id"] = usuario_telegram_id
    resp = db.table("proyectos").insert(data).execute()
    return resp.data[0] if resp.data else None


def get_proyectos(usuario_telegram_id: int, estado: str = None) -> List[Dict]:
    """Lista proyectos de un usuario."""
    db = get_supabase()
    query = db.table("proyectos").select("*, contactos(nombre)")\
        .eq("usuario_telegram_id", usuario_telegram_id)
    
    if estado:
        query = query.eq("estado", estado)
    
    resp = query.order("created_at", desc=True).execute()
    return resp.data or []


def get_proyecto(proyecto_id: int, usuario_telegram_id: int) -> Optional[Dict]:
    """Obtiene un proyecto por ID."""
    db = get_supabase()
    resp = db.table("proyectos").select("*, contactos(nombre)")\
        .eq("id", proyecto_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def update_proyecto(proyecto_id: int, usuario_telegram_id: int, data: Dict) -> Optional[Dict]:
    """Actualiza un proyecto."""
    db = get_supabase()
    resp = db.table("proyectos").update(data)\
        .eq("id", proyecto_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def delete_proyecto(proyecto_id: int, usuario_telegram_id: int) -> bool:
    """Elimina un proyecto."""
    db = get_supabase()
    resp = db.table("proyectos").delete()\
        .eq("id", proyecto_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return len(resp.data) > 0 if resp.data else False


# =============================================
# TAREAS
# =============================================
def create_tarea(usuario_telegram_id: int, data: Dict, recordatorios: List[Dict] = None) -> Dict:
    """Crea una nueva tarea con recordatorios opcionales."""
    db = get_supabase()
    data["usuario_telegram_id"] = usuario_telegram_id
    
    # Crear tarea
    resp = db.table("tareas").insert(data).execute()
    
    if not resp.data:
        raise Exception("Error creando tarea")
    
    tarea = resp.data[0]
    
    # Crear recordatorios si se proporcionan
    if recordatorios:
        for rec in recordatorios:
            rec["tarea_id"] = tarea["id"]
            db.table("recordatorios_config").insert(rec).execute()
    
    return tarea


def get_tareas(
    usuario_telegram_id: int, 
    estado: str = None, 
    contacto_id: int = None,
    proyecto_id: int = None,
    fecha_desde: datetime = None,
    fecha_hasta: datetime = None
) -> List[Dict]:
    """Lista tareas con filtros opcionales."""
    db = get_supabase()
    query = db.table("tareas").select("*, contactos(id, nombre, email), proyectos(id, nombre)")\
        .eq("usuario_telegram_id", usuario_telegram_id)
    
    if estado:
        query = query.eq("estado", estado)
    if contacto_id:
        query = query.eq("contacto_id", contacto_id)
    if proyecto_id:
        query = query.eq("proyecto_id", proyecto_id)
    if fecha_desde:
        query = query.gte("fecha_vencimiento", fecha_desde.isoformat())
    if fecha_hasta:
        query = query.lte("fecha_vencimiento", fecha_hasta.isoformat())
    
    resp = query.order("fecha_vencimiento").execute()
    return resp.data or []


def get_tareas_pendientes_hoy(usuario_telegram_id: int) -> List[Dict]:
    """Obtiene tareas pendientes para hoy."""
    now = datetime.now(TZ)
    inicio_dia = now.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return get_tareas(
        usuario_telegram_id,
        fecha_desde=inicio_dia,
        fecha_hasta=fin_dia
    )


def get_tarea(tarea_id: int, usuario_telegram_id: int) -> Optional[Dict]:
    """Obtiene una tarea por ID."""
    db = get_supabase()
    resp = db.table("tareas").select("*, contactos(id, nombre, email), proyectos(id, nombre)")\
        .eq("id", tarea_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def update_tarea(tarea_id: int, usuario_telegram_id: int, data: Dict) -> Optional[Dict]:
    """Actualiza una tarea."""
    db = get_supabase()
    resp = db.table("tareas").update(data)\
        .eq("id", tarea_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def delete_tarea(tarea_id: int, usuario_telegram_id: int) -> bool:
    """Elimina una tarea."""
    db = get_supabase()
    resp = db.table("tareas").delete()\
        .eq("id", tarea_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return len(resp.data) > 0 if resp.data else False


def cambiar_estado_tarea(tarea_id: int, usuario_telegram_id: int, nuevo_estado: str) -> Optional[Dict]:
    """Cambia el estado de una tarea."""
    return update_tarea(tarea_id, usuario_telegram_id, {"estado": nuevo_estado})


# =============================================
# RECORDATORIOS CONFIG
# =============================================
def get_recordatorios_config(tarea_id: int) -> List[Dict]:
    """Obtiene configuración de recordatorios de una tarea."""
    db = get_supabase()
    resp = db.table("recordatorios_config").select("*")\
        .eq("tarea_id", tarea_id)\
        .eq("activo", True)\
        .order("dias_antes", desc=True)\
        .execute()
    return resp.data or []


def create_recordatorio_config(tarea_id: int, data: Dict) -> Dict:
    """Crea un nuevo recordatorio para una tarea."""
    db = get_supabase()
    data["tarea_id"] = tarea_id
    resp = db.table("recordatorios_config").insert(data).execute()
    return resp.data[0] if resp.data else None


def delete_recordatorio_config(recordatorio_id: int) -> bool:
    """Elimina un recordatorio config."""
    db = get_supabase()
    resp = db.table("recordatorios_config").delete().eq("id", recordatorio_id).execute()
    return len(resp.data) > 0 if resp.data else False


# =============================================
# RECORDATORIOS ENVIADOS (LOG)
# =============================================
def log_recordatorio_enviado(data: Dict) -> Dict:
    """Registra un recordatorio enviado."""
    db = get_supabase()
    resp = db.table("recordatorios_enviados").insert(data).execute()
    return resp.data[0] if resp.data else None


def get_recordatorios_enviados(usuario_telegram_id: int, limit: int = 50) -> List[Dict]:
    """Obtiene historial de recordatorios enviados."""
    db = get_supabase()
    resp = db.table("recordatorios_enviados")\
        .select("*, tareas(id, titulo, usuario_telegram_id)")\
        .order("fecha_envio", desc=True)\
        .limit(limit)\
        .execute()
    
    # Filtrar por usuario (no hay FK directa)
    return [r for r in (resp.data or []) 
            if r.get("tareas", {}).get("usuario_telegram_id") == usuario_telegram_id]


# =============================================
# PLANTILLAS
# =============================================
def create_plantilla(usuario_telegram_id: int, data: Dict) -> Dict:
    """Crea una nueva plantilla."""
    db = get_supabase()
    data["usuario_telegram_id"] = usuario_telegram_id
    resp = db.table("plantillas").insert(data).execute()
    return resp.data[0] if resp.data else None


def get_plantillas(usuario_telegram_id: int, tipo: str = None) -> List[Dict]:
    """Lista plantillas de un usuario."""
    db = get_supabase()
    query = db.table("plantillas").select("*").eq("usuario_telegram_id", usuario_telegram_id)
    
    if tipo:
        query = query.eq("tipo", tipo)
    
    resp = query.order("nombre").execute()
    return resp.data or []


def get_plantilla(plantilla_id: int, usuario_telegram_id: int) -> Optional[Dict]:
    """Obtiene una plantilla por ID."""
    db = get_supabase()
    resp = db.table("plantillas").select("*")\
        .eq("id", plantilla_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def get_plantilla_default(usuario_telegram_id: int, tipo: str) -> Optional[Dict]:
    """Obtiene la plantilla por defecto de un tipo."""
    db = get_supabase()
    resp = db.table("plantillas").select("*")\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .eq("tipo", tipo)\
        .eq("es_default", True)\
        .execute()
    return resp.data[0] if resp.data else None


def update_plantilla(plantilla_id: int, usuario_telegram_id: int, data: Dict) -> Optional[Dict]:
    """Actualiza una plantilla."""
    db = get_supabase()
    resp = db.table("plantillas").update(data)\
        .eq("id", plantilla_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return resp.data[0] if resp.data else None


def delete_plantilla(plantilla_id: int, usuario_telegram_id: int) -> bool:
    """Elimina una plantilla."""
    db = get_supabase()
    resp = db.table("plantillas").delete()\
        .eq("id", plantilla_id)\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .execute()
    return len(resp.data) > 0 if resp.data else False


def create_default_plantillas(usuario_telegram_id: int):
    """Crea plantillas por defecto para un nuevo usuario."""
    db = get_supabase()
    
    plantillas_default = [
        {
            "usuario_telegram_id": usuario_telegram_id,
            "nombre": "Recordatorio Telegram",
            "tipo": "telegram",
            "mensaje": "⏰ *Recordatorio*\n\n📋 *Tarea:* {{titulo}}\n👤 *Contacto:* {{contacto_nombre}}\n📅 *Vencimiento:* {{fecha_vencimiento}}\n\n{{descripcion}}",
            "es_default": True
        },
        {
            "usuario_telegram_id": usuario_telegram_id,
            "nombre": "Recordatorio Email",
            "tipo": "email",
            "asunto": "Recordatorio: {{titulo}}",
            "mensaje": "Hola,\n\nEste es un recordatorio sobre la tarea:\n\n📋 Tarea: {{titulo}}\n👤 Contacto: {{contacto_nombre}}\n📅 Vencimiento: {{fecha_vencimiento}}\n\n{{descripcion}}\n\nSaludos,\nCRM Bot",
            "es_default": True
        },
        {
            "usuario_telegram_id": usuario_telegram_id,
            "nombre": "Follow-up Telegram",
            "tipo": "telegram",
            "mensaje": "📞 *Seguimiento Pendiente*\n\n👤 *Contacto:* {{contacto_nombre}}\n🏢 *Empresa:* {{contacto_empresa}}\n📋 *Asunto:* {{titulo}}\n\nRecuerda hacer follow-up!",
            "es_default": False
        }
    ]
    
    for plantilla in plantillas_default:
        db.table("plantillas").insert(plantilla).execute()


# =============================================
# HISTORIAL
# =============================================
def log_interaccion(usuario_telegram_id: int, data: Dict) -> Dict:
    """Registra una interacción en el historial."""
    db = get_supabase()
    data["usuario_telegram_id"] = usuario_telegram_id
    resp = db.table("historial_interacciones").insert(data).execute()
    return resp.data[0] if resp.data else None


def get_historial_contacto(contacto_id: int, limit: int = 20) -> List[Dict]:
    """Obtiene historial de un contacto."""
    db = get_supabase()
    resp = db.table("historial_interacciones").select("*")\
        .eq("contacto_id", contacto_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    return resp.data or []


# =============================================
# DASHBOARD / ESTADÍSTICAS
# =============================================
def get_dashboard_stats(usuario_telegram_id: int) -> Dict:
    """Obtiene estadísticas para el dashboard."""
    db = get_supabase()
    now = datetime.now(TZ)
    inicio_dia = now.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Total contactos
    contactos = db.table("contactos").select("id", count="exact")\
        .eq("usuario_telegram_id", usuario_telegram_id).execute()
    
    # Tareas por estado
    tareas = db.table("tareas").select("estado")\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .neq("estado", "completado").execute()
    
    tareas_por_estado = {}
    for t in (tareas.data or []):
        estado = t["estado"]
        tareas_por_estado[estado] = tareas_por_estado.get(estado, 0) + 1
    
    # Tareas hoy
    tareas_hoy = db.table("tareas").select("id", count="exact")\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .gte("fecha_vencimiento", inicio_dia.isoformat())\
        .lte("fecha_vencimiento", fin_dia.isoformat()).execute()
    
    # Proyectos activos
    proyectos = db.table("proyectos").select("id", count="exact")\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .eq("estado", "activo").execute()
    
    # Próximos vencimientos (7 días)
    proximos = db.table("tareas").select("*, contactos(nombre)")\
        .eq("usuario_telegram_id", usuario_telegram_id)\
        .neq("estado", "completado")\
        .gte("fecha_vencimiento", now.isoformat())\
        .lte("fecha_vencimiento", (now + timedelta(days=7)).isoformat())\
        .order("fecha_vencimiento")\
        .limit(10).execute()
    
    return {
        "total_contactos": contactos.count or 0,
        "total_tareas_pendientes": len(tareas.data or []),
        "total_tareas_hoy": tareas_hoy.count or 0,
        "total_proyectos_activos": proyectos.count or 0,
        "tareas_por_estado": tareas_por_estado,
        "proximos_vencimientos": proximos.data or []
    }


# =============================================
# RECORDATORIOS - PARA SCHEDULER
# =============================================
def get_recordatorios_pendientes() -> List[Dict]:
    """
    Obtiene recordatorios que deben enviarse.
    Busca tareas activas cuyos recordatorios configurados coinciden con hoy.
    """
    db = get_supabase()
    now = datetime.now(TZ)
    hoy = now.date()
    
    # Obtener todas las tareas activas con fecha de vencimiento
    # Nota: usuarios.email se usa para Reply-To y CC en emails
    tareas = db.table("tareas")\
        .select("*, contactos(id, nombre, email, telegram_id), usuarios(telegram_id, email), recordatorios_config(*)")\
        .neq("estado", "completado")\
        .not_.is_("fecha_vencimiento", "null")\
        .execute()
    
    pendientes = []
    
    for tarea in (tareas.data or []):
        if not tarea.get("recordatorios_config"):
            continue
        
        fecha_vencimiento = datetime.fromisoformat(tarea["fecha_vencimiento"].replace("Z", "+00:00"))
        if fecha_vencimiento.tzinfo is None:
            fecha_vencimiento = TZ.localize(fecha_vencimiento)
        
        for rec_config in tarea["recordatorios_config"]:
            if not rec_config.get("activo"):
                continue
            
            # Calcular fecha del recordatorio
            dias_antes = rec_config.get("dias_antes", 0)
            fecha_recordatorio = (fecha_vencimiento - timedelta(days=dias_antes)).date()
            
            # Si es hoy
            if fecha_recordatorio == hoy:
                hora_rec = rec_config.get("hora", "09:00")
                if isinstance(hora_rec, str):
                    hora_rec = datetime.strptime(hora_rec, "%H:%M:%S").time()
                
                # Verificar si ya pasó la hora (o estamos cerca)
                rec_datetime = TZ.localize(datetime.combine(hoy, hora_rec))
                
                if now >= rec_datetime:
                    # Verificar que no se haya enviado ya hoy
                    ya_enviado = db.table("recordatorios_enviados")\
                        .select("id")\
                        .eq("recordatorio_config_id", rec_config["id"])\
                        .gte("fecha_envio", datetime.combine(hoy, time.min).isoformat())\
                        .execute()
                    
                    if not ya_enviado.data:
                        pendientes.append({
                            "tarea": tarea,
                            "recordatorio_config": rec_config,
                            "usuario": tarea.get("usuarios"),
                            "contacto": tarea.get("contactos")
                        })
    
    return pendientes
