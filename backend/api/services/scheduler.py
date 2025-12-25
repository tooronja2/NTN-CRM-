"""
Scheduler - Servicio de automatización y cron jobs (SaaS)
=========================================================
Procesa recordatorios usando SMTP centralizado.
El email del usuario va en Reply-To y CC.
"""
import logging
from datetime import datetime, timedelta, time
from typing import Dict, Any, List

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .database import (
    get_recordatorios_pendientes,
    log_recordatorio_enviado,
    get_plantilla_default,
    update_tarea,
    log_interaccion,
    get_usuario
)
from .email_service import send_reminder_email
from .telegram_service import send_reminder_telegram

logger = logging.getLogger(__name__)

# Scheduler global
scheduler: AsyncIOScheduler = None


def get_scheduler() -> AsyncIOScheduler:
    """Obtiene el scheduler singleton."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


async def process_pending_reminders():
    """
    Procesa todos los recordatorios pendientes.
    Esta función se ejecuta periódicamente (cada minuto).
    """
    try:
        logger.info("🔍 Verificando recordatorios pendientes...")
        
        pendientes = get_recordatorios_pendientes()
        
        if not pendientes:
            logger.debug("No hay recordatorios pendientes")
            return
        
        logger.info(f"📋 {len(pendientes)} recordatorios para enviar")
        
        for item in pendientes:
            await send_single_reminder(item)
    
    except Exception as e:
        logger.error(f"❌ Error en process_pending_reminders: {e}")


async def send_single_reminder(item: Dict) -> Dict[str, Any]:
    """
    Envía un único recordatorio por el canal configurado.
    
    Para emails:
    - Sale del dominio centralizado del CRM
    - Reply-To apunta al email del usuario
    - El usuario va en CC
    """
    tarea = item["tarea"]
    rec_config = item["recordatorio_config"]
    usuario = item["usuario"]
    contacto = item["contacto"]
    
    canal = rec_config.get("canal", "telegram")
    resultados = []
    
    usuario_telegram_id = tarea.get("usuario_telegram_id")
    
    # Obtener email del usuario para Reply-To y CC
    usuario_email = usuario.get("email") if usuario else None
    
    try:
        # Enviar por Telegram
        if canal in ["telegram", "ambos"]:
            # Obtener plantilla
            plantilla = get_plantilla_default(usuario_telegram_id, "telegram")
            if not plantilla:
                plantilla = {"mensaje": "⏰ *Recordatorio*\n\n📋 *{{titulo}}*\n{{descripcion}}"}
            
            result = send_reminder_telegram(
                chat_id=usuario_telegram_id,  # Enviar al PM
                tarea=tarea,
                contacto=contacto,
                plantilla=plantilla
            )
            
            # Loggear
            log_recordatorio_enviado({
                "tarea_id": tarea["id"],
                "recordatorio_config_id": rec_config["id"],
                "canal": "telegram",
                "estado": "enviado" if result["success"] else "fallido",
                "mensaje": plantilla.get("mensaje", ""),
                "error_mensaje": result.get("error")
            })
            
            resultados.append({"canal": "telegram", **result})
        
        # Enviar por Email (desde dominio centralizado)
        if canal in ["email", "ambos"]:
            if contacto and contacto.get("email"):
                plantilla = get_plantilla_default(usuario_telegram_id, "email")
                if not plantilla:
                    plantilla = {
                        "asunto": "Recordatorio: {{titulo}}",
                        "mensaje": "Hola {{contacto_nombre}},\n\nEste es un recordatorio sobre:\n\n📋 {{titulo}}\n📅 Fecha: {{fecha_vencimiento}}\n\n{{descripcion}}\n\nSaludos"
                    }
                
                # Enviar email con Reply-To y CC al usuario
                result = send_reminder_email(
                    tarea=tarea,
                    contacto=contacto,
                    plantilla=plantilla,
                    usuario_email=usuario_email  # Para Reply-To y CC
                )
                
                # Loggear
                log_recordatorio_enviado({
                    "tarea_id": tarea["id"],
                    "recordatorio_config_id": rec_config["id"],
                    "canal": "email",
                    "estado": "enviado" if result["success"] else "fallido",
                    "mensaje": f"A: {contacto['email']}, CC: {usuario_email}",
                    "error_mensaje": result.get("error")
                })
                
                resultados.append({"canal": "email", **result})
            else:
                logger.warning(f"Tarea {tarea['id']}: contacto sin email, no se envió por email")
        
        # Registrar en historial
        if contacto:
            log_interaccion(usuario_telegram_id, {
                "contacto_id": contacto.get("id"),
                "tarea_id": tarea["id"],
                "tipo": "recordatorio_enviado",
                "descripcion": f"Recordatorio enviado: {tarea.get('titulo')}",
                "metadata": {
                    "canales": [r["canal"] for r in resultados],
                    "usuario_email_cc": usuario_email
                }
            })
        
        return {"success": True, "resultados": resultados}
    
    except Exception as e:
        logger.error(f"❌ Error enviando recordatorio tarea {tarea.get('id')}: {e}")
        return {"success": False, "error": str(e)}


def start_scheduler():
    """
    Inicia el scheduler de tareas.
    """
    global scheduler
    scheduler = get_scheduler()
    
    # Job cada minuto para revisar recordatorios
    scheduler.add_job(
        process_pending_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="check_reminders",
        name="Verificar recordatorios pendientes",
        replace_existing=True
    )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("⏰ Scheduler iniciado")


def stop_scheduler():
    """
    Detiene el scheduler.
    """
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("⏰ Scheduler detenido")


async def trigger_manual_check():
    """
    Dispara una verificación manual de recordatorios.
    Útil para testing.
    """
    await process_pending_reminders()
    return {"success": True, "message": "Verificación completada"}
