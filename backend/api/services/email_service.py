"""
Servicio de Email - SMTP Centralizado (SaaS)
=============================================
Todos los emails salen del dominio del CRM.
El email del usuario va en Reply-To y CC para recibir respuestas.
"""
import os
import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
import re

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# =============================================
# CONFIGURACIÓN CENTRALIZADA (del servidor/dominio)
# =============================================
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")  # noreply@tudominio.com
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "CRM Follow-Up")
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "true").lower() == "true"


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Renderiza una plantilla reemplazando variables.
    Variables en formato: {{nombre_variable}}
    """
    result = template
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value) if value else "")
    
    # Limpiar variables no reemplazadas
    result = re.sub(r'\{\{[^}]+\}\}', '', result)
    
    return result


def send_email_sync(
    to: str,
    subject: str,
    body: str,
    reply_to: str = None,
    cc: List[str] = None,
    is_html: bool = False
) -> Dict[str, Any]:
    """
    Envía un email usando el SMTP centralizado del servidor.
    
    Args:
        to: Destinatario principal
        subject: Asunto del email
        body: Contenido del email
        reply_to: Email al que responder (el del usuario del CRM)
        cc: Lista de emails en copia (incluye al usuario del CRM)
        is_html: Si el contenido es HTML
    
    Returns:
        Dict con success y mensaje/error
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return {
            "success": False,
            "error": "SMTP no configurado en el servidor. Contacta al administrador."
        }
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg['To'] = to
        
        # Reply-To: el email del usuario del CRM
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # CC: incluir al usuario para que vea los envíos
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        # Agregar contenido
        if is_html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Lista completa de destinatarios
        all_recipients = [to]
        if cc:
            all_recipients.extend(cc)
        
        # Enviar
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg, to_addrs=all_recipients)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg, to_addrs=all_recipients)
        
        logger.info(f"📧 Email enviado a {to} (reply-to: {reply_to}, cc: {cc})")
        return {"success": True, "message": f"Email enviado a {to}"}
    
    except smtplib.SMTPAuthenticationError:
        error_msg = "Error de autenticación SMTP. Verificar credenciales del servidor."
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}
    
    except Exception as e:
        error_msg = f"Error enviando email: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


async def send_email(
    to: str,
    subject: str,
    body: str,
    reply_to: str = None,
    cc: List[str] = None,
    is_html: bool = False
) -> Dict[str, Any]:
    """Versión asíncrona de send_email_sync."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: send_email_sync(to, subject, body, reply_to, cc, is_html)
    )


def send_reminder_email(
    tarea: Dict,
    contacto: Dict,
    plantilla: Dict,
    usuario_email: str = None
) -> Dict[str, Any]:
    """
    Envía un email de recordatorio usando plantilla.
    
    El email sale del dominio del CRM pero:
    - Reply-To apunta al email del usuario
    - El usuario va en CC para ver el envío
    
    Args:
        tarea: Datos de la tarea
        contacto: Datos del contacto (destinatario)
        plantilla: Plantilla a usar
        usuario_email: Email del usuario del CRM (para Reply-To y CC)
    """
    if not contacto.get("email"):
        return {"success": False, "error": "Contacto sin email configurado"}
    
    # Preparar variables
    variables = {
        "titulo": tarea.get("titulo", ""),
        "descripcion": tarea.get("descripcion", ""),
        "fecha_vencimiento": tarea.get("fecha_vencimiento", "")[:10] if tarea.get("fecha_vencimiento") else "",
        "contacto_nombre": contacto.get("nombre", ""),
        "contacto_email": contacto.get("email", ""),
        "contacto_empresa": contacto.get("empresa", ""),
        "prioridad": tarea.get("prioridad", ""),
        "estado": tarea.get("estado", ""),
    }
    
    # Renderizar plantilla
    asunto = render_template(plantilla.get("asunto", "Recordatorio: {{titulo}}"), variables)
    mensaje = render_template(plantilla.get("mensaje", ""), variables)
    
    # Agregar firma automática si el usuario tiene email
    if usuario_email:
        mensaje += f"\n\n---\nPuedes responder directamente a este email."
    
    return send_email_sync(
        to=contacto["email"],
        subject=asunto,
        body=mensaje,
        reply_to=usuario_email,
        cc=[usuario_email] if usuario_email else None
    )


def test_smtp_connection() -> Dict[str, Any]:
    """
    Prueba la conexión SMTP del servidor.
    Útil para verificar configuración.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return {"success": False, "error": "SMTP no configurado"}
    
    try:
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
        
        return {"success": True, "message": "Conexión SMTP exitosa"}
    
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "error": "Credenciales SMTP inválidas"}
    
    except Exception as e:
        return {"success": False, "error": f"Error de conexión: {str(e)}"}


def get_smtp_status() -> Dict[str, Any]:
    """Retorna el estado de configuración SMTP."""
    return {
        "configured": bool(SMTP_USER and SMTP_PASSWORD),
        "host": SMTP_HOST,
        "port": SMTP_PORT,
        "from_email": SMTP_USER,
        "from_name": SMTP_FROM_NAME,
        "ssl": SMTP_USE_SSL
    }
