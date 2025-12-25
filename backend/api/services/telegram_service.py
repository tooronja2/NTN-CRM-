"""
Servicio de Telegram - Envío de notificaciones
"""
import os
import logging
from typing import Dict, Any, Optional
import httpx

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


async def send_telegram_message(
    chat_id: int,
    text: str,
    parse_mode: str = "Markdown",
    reply_markup: Dict = None
) -> Dict[str, Any]:
    """
    Envía un mensaje de Telegram.
    """
    if not TELEGRAM_TOKEN:
        return {"success": False, "error": "TELEGRAM_TOKEN no configurado"}
    
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json=payload,
                timeout=30
            )
            result = response.json()
        
        if result.get("ok"):
            logger.info(f"📱 Telegram enviado a {chat_id}")
            return {
                "success": True,
                "message_id": result["result"]["message_id"]
            }
        else:
            error = result.get("description", "Error desconocido")
            logger.error(f"❌ Error Telegram: {error}")
            return {"success": False, "error": error}
    
    except Exception as e:
        error_msg = f"Error enviando Telegram: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def send_telegram_message_sync(
    chat_id: int,
    text: str,
    parse_mode: str = "Markdown"
) -> Dict[str, Any]:
    """
    Versión síncrona para usar en contextos no-async.
    """
    import requests
    
    if not TELEGRAM_TOKEN:
        return {"success": False, "error": "TELEGRAM_TOKEN no configurado"}
    
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        response = requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json=payload,
            timeout=30
        )
        result = response.json()
        
        if result.get("ok"):
            logger.info(f"📱 Telegram enviado a {chat_id}")
            return {
                "success": True,
                "message_id": result["result"]["message_id"]
            }
        else:
            error = result.get("description", "Error desconocido")
            logger.error(f"❌ Error Telegram: {error}")
            return {"success": False, "error": error}
    
    except Exception as e:
        error_msg = f"Error enviando Telegram: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def render_telegram_message(
    tarea: Dict,
    contacto: Dict,
    plantilla: Dict
) -> str:
    """
    Renderiza un mensaje de Telegram usando plantilla.
    """
    from .email_service import render_template
    
    variables = {
        "titulo": tarea.get("titulo", ""),
        "descripcion": tarea.get("descripcion", ""),
        "fecha_vencimiento": tarea.get("fecha_vencimiento", "")[:10] if tarea.get("fecha_vencimiento") else "",
        "contacto_nombre": contacto.get("nombre", "") if contacto else "",
        "contacto_email": contacto.get("email", "") if contacto else "",
        "contacto_empresa": contacto.get("empresa", "") if contacto else "",
        "prioridad": tarea.get("prioridad", ""),
        "estado": tarea.get("estado", ""),
    }
    
    return render_template(plantilla.get("mensaje", "⏰ Recordatorio: {{titulo}}"), variables)


def send_reminder_telegram(
    chat_id: int,
    tarea: Dict,
    contacto: Dict,
    plantilla: Dict
) -> Dict[str, Any]:
    """
    Envía un recordatorio de Telegram usando plantilla.
    """
    mensaje = render_telegram_message(tarea, contacto, plantilla)
    return send_telegram_message_sync(chat_id, mensaje)


async def set_webhook(webhook_url: str) -> Dict[str, Any]:
    """
    Configura el webhook de Telegram.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_URL}/setWebhook",
                json={"url": webhook_url},
                timeout=30
            )
            result = response.json()
        
        if result.get("ok"):
            logger.info(f"✅ Webhook configurado: {webhook_url}")
            return {"success": True}
        else:
            return {"success": False, "error": result.get("description")}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


async def delete_webhook() -> Dict[str, Any]:
    """
    Elimina el webhook de Telegram (para usar polling).
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_URL}/deleteWebhook",
                timeout=30
            )
            result = response.json()
        
        if result.get("ok"):
            logger.info("✅ Webhook eliminado")
            return {"success": True}
        else:
            return {"success": False, "error": result.get("description")}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
