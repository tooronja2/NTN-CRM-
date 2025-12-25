"""
CRM Follow-Up Automation - Bot de Telegram Completo
====================================================
Bot con gestión de contactos, tareas, proyectos desde Telegram
"""
import os
import re
import logging
import datetime
from typing import Optional, Dict, Any

import pytz
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters
)

# Importar servicios
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.database import (
    get_or_create_usuario, get_usuario, update_usuario,
    create_contacto, get_contactos, get_contacto, delete_contacto,
    create_tarea, get_tareas, get_tarea, update_tarea, delete_tarea,
    get_tareas_pendientes_hoy, cambiar_estado_tarea,
    create_proyecto, get_proyectos, get_proyecto,
    get_plantillas, get_dashboard_stats,
    create_recordatorio_config
)
from api.services.email_service import test_gmail_connection
from api.services.scheduler import start_scheduler, process_pending_reminders

load_dotenv()

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TZ = pytz.timezone(os.getenv("TIMEZONE", "America/Argentina/Buenos_Aires"))

# Estados para ConversationHandler
(
    CONTACTO_NOMBRE, CONTACTO_EMAIL, CONTACTO_TELEFONO, CONTACTO_EMPRESA,
    TAREA_TITULO, TAREA_CONTACTO, TAREA_FECHA, TAREA_HORA, TAREA_DESCRIPCION,
    PROYECTO_NOMBRE, PROYECTO_DESCRIPCION, PROYECTO_CONTACTO,
    CONFIG_EMAIL_USER, CONFIG_EMAIL_PASSWORD
) = range(14)

# Mapeo de días
DIAS_SEMANA = {
    'lunes': MO, 'lun': MO,
    'martes': TU, 'mar': TU,
    'miércoles': WE, 'miercoles': WE, 'mie': WE,
    'jueves': TH, 'jue': TH,
    'viernes': FR, 'vie': FR,
    'sábado': SA, 'sabado': SA, 'sab': SA,
    'domingo': SU, 'dom': SU,
}


# =============================================
# COMANDOS BÁSICOS
# =============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Registro y bienvenida."""
    user = update.effective_user
    telegram_id = user.id
    nombre = user.full_name or user.username or "Usuario"
    
    # Registrar usuario
    get_or_create_usuario(telegram_id, nombre)
    
    welcome_text = f"""
👋 *¡Hola {nombre}!*

Soy tu *CRM de Follow-Up*, tu asistente para gestionar contactos, tareas y recordatorios.

📋 *Comandos principales:*

*Contactos:*
• /contactos - Ver lista de contactos
• /nuevo\\_contacto - Crear contacto
• /buscar \\[nombre\\] - Buscar contacto

*Tareas:*
• /tareas - Ver tareas pendientes
• /hoy - Tareas de hoy
• /nueva\\_tarea - Crear tarea
• /completar \\[id\\] - Completar tarea

*Proyectos:*
• /proyectos - Ver proyectos
• /nuevo\\_proyecto - Crear proyecto

*Recordatorios rápidos:*
• Escribe: "recordame mañana 10hs llamar a Juan"

*Configuración:*
• /config\\_email - Configurar Gmail
• /resumen - Ver resumen general
• /ayuda - Ver esta ayuda

🌐 También puedes usar la *Web* para gestión visual.
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda."""
    await start_command(update, context)


async def resumen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /resumen - Dashboard rápido."""
    telegram_id = update.effective_user.id
    
    try:
        stats = get_dashboard_stats(telegram_id)
        
        resumen = f"""
📊 *Tu Resumen*

👥 *Contactos:* {stats['total_contactos']}
📋 *Tareas pendientes:* {stats['total_tareas_pendientes']}
📅 *Tareas hoy:* {stats['total_tareas_hoy']}
🗂 *Proyectos activos:* {stats['total_proyectos_activos']}

📈 *Por estado:*
"""
        for estado, count in stats['tareas_por_estado'].items():
            emoji = {'pendiente': '🔴', 'en_seguimiento': '🟡', 'esperando_respuesta': '🟠', 'completado': '🟢'}.get(estado, '⚪')
            resumen += f"  {emoji} {estado.replace('_', ' ').title()}: {count}\n"
        
        if stats['proximos_vencimientos']:
            resumen += "\n📅 *Próximos vencimientos:*\n"
            for t in stats['proximos_vencimientos'][:5]:
                fecha = t.get('fecha_vencimiento', '')[:10] if t.get('fecha_vencimiento') else 'Sin fecha'
                resumen += f"  • {t['titulo']} ({fecha})\n"
        
        await update.message.reply_text(resumen, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en resumen: {e}")
        await update.message.reply_text("❌ Error obteniendo resumen")


# =============================================
# CONTACTOS
# =============================================

async def contactos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /contactos - Listar contactos."""
    telegram_id = update.effective_user.id
    
    contactos = get_contactos(telegram_id)
    
    if not contactos:
        await update.message.reply_text(
            "📭 No tienes contactos aún.\n\nUsa /nuevo\\_contacto para crear uno.",
            parse_mode='Markdown'
        )
        return
    
    text = "👥 *Tus Contactos:*\n\n"
    for i, c in enumerate(contactos[:20], 1):
        email_icon = "📧" if c.get('email') else ""
        tg_icon = "📱" if c.get('telegram_id') else ""
        text += f"{i}. *{c['nombre']}* {email_icon}{tg_icon}\n"
        if c.get('empresa'):
            text += f"   🏢 {c['empresa']}\n"
    
    if len(contactos) > 20:
        text += f"\n_...y {len(contactos) - 20} más_"
    
    text += "\n\nUsa /contacto\\_\\[número\\] para ver detalles"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def buscar_contacto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /buscar [nombre] - Buscar contacto."""
    telegram_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Uso: /buscar \\[nombre\\]", parse_mode='Markdown')
        return
    
    search = ' '.join(context.args)
    contactos = get_contactos(telegram_id, search)
    
    if not contactos:
        await update.message.reply_text(f"No se encontraron contactos con '{search}'")
        return
    
    text = f"🔍 *Resultados para '{search}':*\n\n"
    for c in contactos[:10]:
        text += f"• *{c['nombre']}*"
        if c.get('empresa'):
            text += f" ({c['empresa']})"
        text += f" - ID: {c['id']}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def nuevo_contacto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de nuevo contacto."""
    await update.message.reply_text(
        "👤 *Nuevo Contacto*\n\n¿Cuál es el *nombre* del contacto?",
        parse_mode='Markdown'
    )
    return CONTACTO_NOMBRE


async def nuevo_contacto_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda nombre y pide email."""
    context.user_data['nuevo_contacto'] = {'nombre': update.message.text}
    
    keyboard = [[InlineKeyboardButton("⏭ Omitir", callback_data="skip_email")]]
    await update.message.reply_text(
        "📧 ¿Cuál es su *email*? (o presiona Omitir)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONTACTO_EMAIL


async def nuevo_contacto_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda email y pide teléfono."""
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['nuevo_contacto']['email'] = None
    else:
        context.user_data['nuevo_contacto']['email'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("⏭ Omitir", callback_data="skip_telefono")]]
    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text(
        "📞 ¿Cuál es su *teléfono*? (o presiona Omitir)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONTACTO_TELEFONO


async def nuevo_contacto_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda teléfono y pide empresa."""
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['nuevo_contacto']['telefono'] = None
    else:
        context.user_data['nuevo_contacto']['telefono'] = update.message.text
    
    keyboard = [[InlineKeyboardButton("⏭ Omitir", callback_data="skip_empresa")]]
    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text(
        "🏢 ¿Cuál es su *empresa*? (o presiona Omitir)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONTACTO_EMPRESA


async def nuevo_contacto_empresa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda empresa y crea el contacto."""
    telegram_id = update.effective_user.id
    
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['nuevo_contacto']['empresa'] = None
    else:
        context.user_data['nuevo_contacto']['empresa'] = update.message.text
    
    data = context.user_data['nuevo_contacto']
    
    try:
        contacto = create_contacto(telegram_id, data)
        
        msg = update.callback_query.message if update.callback_query else update.message
        await msg.reply_text(
            f"✅ *Contacto creado*\n\n"
            f"👤 {contacto['nombre']}\n"
            f"{'📧 ' + contacto['email'] if contacto.get('email') else ''}\n"
            f"{'📞 ' + contacto['telefono'] if contacto.get('telefono') else ''}\n"
            f"{'🏢 ' + contacto['empresa'] if contacto.get('empresa') else ''}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error creando contacto: {e}")
        msg = update.callback_query.message if update.callback_query else update.message
        await msg.reply_text("❌ Error creando contacto")
    
    context.user_data.pop('nuevo_contacto', None)
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela cualquier conversación."""
    context.user_data.clear()
    await update.message.reply_text("❌ Operación cancelada")
    return ConversationHandler.END


# =============================================
# TAREAS
# =============================================

async def tareas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /tareas - Listar tareas pendientes."""
    telegram_id = update.effective_user.id
    
    tareas = get_tareas(telegram_id)
    tareas_activas = [t for t in tareas if t.get('estado') != 'completado']
    
    if not tareas_activas:
        await update.message.reply_text(
            "📭 No tienes tareas pendientes.\n\nUsa /nueva\\_tarea para crear una.",
            parse_mode='Markdown'
        )
        return
    
    text = "📋 *Tus Tareas Pendientes:*\n\n"
    
    estados_emoji = {
        'pendiente': '🔴',
        'en_seguimiento': '🟡',
        'esperando_respuesta': '🟠'
    }
    
    for t in tareas_activas[:15]:
        emoji = estados_emoji.get(t.get('estado', 'pendiente'), '⚪')
        fecha = t.get('fecha_vencimiento', '')[:10] if t.get('fecha_vencimiento') else 'Sin fecha'
        
        text += f"{emoji} *{t['titulo']}* (ID: {t['id']})\n"
        text += f"   📅 {fecha}"
        
        if t.get('contactos'):
            text += f" | 👤 {t['contactos']['nombre']}"
        text += "\n"
    
    if len(tareas_activas) > 15:
        text += f"\n_...y {len(tareas_activas) - 15} más_"
    
    text += "\n\n• /completar \\[id\\] - Marcar completada\n• /tarea \\[id\\] - Ver detalles"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def tareas_hoy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /hoy - Tareas de hoy."""
    telegram_id = update.effective_user.id
    
    tareas = get_tareas_pendientes_hoy(telegram_id)
    
    if not tareas:
        await update.message.reply_text("✨ No tienes tareas para hoy. ¡Buen trabajo!")
        return
    
    text = "📅 *Tareas para Hoy:*\n\n"
    for t in tareas:
        estado_emoji = {'pendiente': '🔴', 'en_seguimiento': '🟡', 'esperando_respuesta': '🟠', 'completado': '🟢'}.get(t.get('estado'), '⚪')
        text += f"{estado_emoji} *{t['titulo']}* (ID: {t['id']})\n"
        if t.get('descripcion'):
            text += f"   _{t['descripcion'][:50]}..._\n" if len(t.get('descripcion', '')) > 50 else f"   _{t['descripcion']}_\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def completar_tarea_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /completar [id] - Marcar tarea como completada."""
    telegram_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Uso: /completar \\[id\\_tarea\\]", parse_mode='Markdown')
        return
    
    try:
        tarea_id = int(context.args[0])
        result = cambiar_estado_tarea(tarea_id, telegram_id, 'completado')
        
        if result:
            await update.message.reply_text(f"✅ Tarea #{tarea_id} marcada como completada")
        else:
            await update.message.reply_text("❌ Tarea no encontrada")
    except ValueError:
        await update.message.reply_text("❌ ID inválido")


async def nueva_tarea_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de nueva tarea."""
    await update.message.reply_text(
        "📋 *Nueva Tarea*\n\n¿Cuál es el *título* de la tarea?",
        parse_mode='Markdown'
    )
    return TAREA_TITULO


async def nueva_tarea_titulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda título y pregunta contacto."""
    telegram_id = update.effective_user.id
    context.user_data['nueva_tarea'] = {'titulo': update.message.text}
    
    contactos = get_contactos(telegram_id)
    
    if contactos:
        keyboard = [[InlineKeyboardButton(c['nombre'], callback_data=f"contacto_{c['id']}")] for c in contactos[:5]]
        keyboard.append([InlineKeyboardButton("⏭ Sin contacto", callback_data="contacto_none")])
        
        await update.message.reply_text(
            "👤 ¿Asociar a un *contacto*?",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        context.user_data['nueva_tarea']['contacto_id'] = None
        await update.message.reply_text(
            "📅 ¿Cuál es la *fecha de vencimiento*?\n\nEjemplos: mañana, 25/12, lunes",
            parse_mode='Markdown'
        )
        return TAREA_FECHA
    
    return TAREA_CONTACTO


async def nueva_tarea_contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda contacto y pregunta fecha."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "contacto_none":
        context.user_data['nueva_tarea']['contacto_id'] = None
    else:
        contacto_id = int(query.data.split('_')[1])
        context.user_data['nueva_tarea']['contacto_id'] = contacto_id
    
    await query.message.reply_text(
        "📅 ¿Cuál es la *fecha de vencimiento*?\n\nEjemplos: mañana, 25/12, lunes, hoy",
        parse_mode='Markdown'
    )
    return TAREA_FECHA


async def nueva_tarea_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parsea fecha y pregunta hora."""
    text = update.message.text.lower()
    now = datetime.datetime.now(TZ)
    
    fecha = None
    
    # Parsear fecha
    if 'hoy' in text:
        fecha = now.date()
    elif 'mañana' in text or 'manana' in text:
        fecha = (now + datetime.timedelta(days=1)).date()
    else:
        # Buscar DD/MM
        match = re.search(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?', text)
        if match:
            day, month = int(match.group(1)), int(match.group(2))
            year = int(match.group(3)) if match.group(3) else now.year
            if year < 100:
                year += 2000
            try:
                fecha = datetime.date(year, month, day)
            except ValueError:
                pass
        else:
            # Buscar día de la semana
            for dia_nombre, dia_rel in DIAS_SEMANA.items():
                if dia_nombre in text:
                    next_day = now + relativedelta(weekday=dia_rel(+1))
                    fecha = next_day.date()
                    break
    
    if not fecha:
        fecha = now.date()
    
    context.user_data['nueva_tarea']['fecha'] = fecha
    
    keyboard = [
        [InlineKeyboardButton("9:00", callback_data="hora_09:00"),
         InlineKeyboardButton("10:00", callback_data="hora_10:00"),
         InlineKeyboardButton("12:00", callback_data="hora_12:00")],
        [InlineKeyboardButton("15:00", callback_data="hora_15:00"),
         InlineKeyboardButton("17:00", callback_data="hora_17:00"),
         InlineKeyboardButton("⏭ Sin hora", callback_data="hora_none")]
    ]
    
    await update.message.reply_text(
        f"📅 Fecha: *{fecha.strftime('%d/%m/%Y')}*\n\n🕐 ¿A qué *hora*?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TAREA_HORA


async def nueva_tarea_hora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda hora y pregunta descripción."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "hora_none":
        context.user_data['nueva_tarea']['hora'] = datetime.time(9, 0)
    else:
        hora_str = query.data.split('_')[1]
        hora, minuto = map(int, hora_str.split(':'))
        context.user_data['nueva_tarea']['hora'] = datetime.time(hora, minuto)
    
    keyboard = [[InlineKeyboardButton("⏭ Sin descripción", callback_data="desc_none")]]
    
    await query.message.reply_text(
        "📝 ¿Alguna *descripción* adicional? (o presiona Omitir)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TAREA_DESCRIPCION


async def nueva_tarea_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda descripción y crea la tarea."""
    telegram_id = update.effective_user.id
    
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['nueva_tarea']['descripcion'] = None
        msg = update.callback_query.message
    else:
        context.user_data['nueva_tarea']['descripcion'] = update.message.text
        msg = update.message
    
    data = context.user_data['nueva_tarea']
    
    # Construir fecha_vencimiento
    fecha = data['fecha']
    hora = data['hora']
    fecha_vencimiento = TZ.localize(datetime.datetime.combine(fecha, hora))
    
    try:
        tarea_data = {
            'titulo': data['titulo'],
            'descripcion': data.get('descripcion'),
            'contacto_id': data.get('contacto_id'),
            'fecha_vencimiento': fecha_vencimiento.isoformat(),
            'estado': 'pendiente',
            'prioridad': 'media',
            'canal_notificacion': 'telegram'
        }
        
        tarea = create_tarea(telegram_id, tarea_data)
        
        # Crear recordatorio por defecto (1 día antes)
        create_recordatorio_config(tarea['id'], {
            'dias_antes': 1,
            'hora': '09:00:00',
            'canal': 'telegram'
        })
        
        # Crear recordatorio el mismo día
        create_recordatorio_config(tarea['id'], {
            'dias_antes': 0,
            'hora': hora.strftime('%H:%M:%S'),
            'canal': 'telegram'
        })
        
        await msg.reply_text(
            f"✅ *Tarea creada* (ID: {tarea['id']})\n\n"
            f"📋 *{tarea['titulo']}*\n"
            f"📅 {fecha.strftime('%d/%m/%Y')} a las {hora.strftime('%H:%M')}\n"
            f"🔔 Recordatorios: 1 día antes y el mismo día",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error creando tarea: {e}")
        await msg.reply_text("❌ Error creando tarea")
    
    context.user_data.pop('nueva_tarea', None)
    return ConversationHandler.END


# =============================================
# PROYECTOS
# =============================================

async def proyectos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /proyectos - Listar proyectos."""
    telegram_id = update.effective_user.id
    
    proyectos = get_proyectos(telegram_id)
    
    if not proyectos:
        await update.message.reply_text(
            "📭 No tienes proyectos aún.\n\nUsa /nuevo\\_proyecto para crear uno.",
            parse_mode='Markdown'
        )
        return
    
    text = "🗂 *Tus Proyectos:*\n\n"
    
    estados_emoji = {'activo': '🟢', 'pausado': '🟡', 'completado': '✅', 'cancelado': '❌'}
    
    for p in proyectos[:15]:
        emoji = estados_emoji.get(p.get('estado', 'activo'), '⚪')
        text += f"{emoji} *{p['nombre']}* (ID: {p['id']})\n"
        if p.get('descripcion'):
            text += f"   _{p['descripcion'][:40]}..._\n" if len(p.get('descripcion', '')) > 40 else f"   _{p['descripcion']}_\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def nuevo_proyecto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el wizard de nuevo proyecto."""
    await update.message.reply_text(
        "🗂 *Nuevo Proyecto*\n\n¿Cuál es el *nombre* del proyecto?",
        parse_mode='Markdown'
    )
    return PROYECTO_NOMBRE


async def nuevo_proyecto_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda nombre y pide descripción."""
    context.user_data['nuevo_proyecto'] = {'nombre': update.message.text}
    
    keyboard = [[InlineKeyboardButton("⏭ Omitir", callback_data="skip_desc_proyecto")]]
    await update.message.reply_text(
        "📝 ¿Alguna *descripción*? (o presiona Omitir)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROYECTO_DESCRIPCION


async def nuevo_proyecto_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda descripción y crea proyecto."""
    telegram_id = update.effective_user.id
    
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['nuevo_proyecto']['descripcion'] = None
        msg = update.callback_query.message
    else:
        context.user_data['nuevo_proyecto']['descripcion'] = update.message.text
        msg = update.message
    
    data = context.user_data['nuevo_proyecto']
    
    try:
        proyecto = create_proyecto(telegram_id, data)
        
        await msg.reply_text(
            f"✅ *Proyecto creado* (ID: {proyecto['id']})\n\n"
            f"🗂 *{proyecto['nombre']}*\n"
            f"{('📝 ' + proyecto['descripcion']) if proyecto.get('descripcion') else ''}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error creando proyecto: {e}")
        await msg.reply_text("❌ Error creando proyecto")
    
    context.user_data.pop('nuevo_proyecto', None)
    return ConversationHandler.END


# =============================================
# CONFIGURACIÓN EMAIL
# =============================================

async def config_email_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia configuración de Gmail."""
    await update.message.reply_text(
        "📧 *Configurar Gmail SMTP*\n\n"
        "Para enviar emails automáticos, necesitas:\n"
        "1. Tu email de Gmail\n"
        "2. Una 'App Password' de Google\n\n"
        "📖 Para crear una App Password:\n"
        "• Ir a myaccount.google.com/security\n"
        "• Activar verificación en 2 pasos\n"
        "• Crear App Password para 'Mail'\n\n"
        "¿Cuál es tu *email de Gmail*?",
        parse_mode='Markdown'
    )
    return CONFIG_EMAIL_USER


async def config_email_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda email y pide password."""
    email = update.message.text
    
    if '@gmail.com' not in email.lower():
        await update.message.reply_text("⚠️ Debe ser un email de Gmail (@gmail.com)")
        return CONFIG_EMAIL_USER
    
    context.user_data['config_email'] = {'gmail_user': email}
    
    await update.message.reply_text(
        "🔑 Ahora ingresa tu *App Password*\n\n"
        "_(Es un código de 16 caracteres, ej: xxxx xxxx xxxx xxxx)_",
        parse_mode='Markdown'
    )
    return CONFIG_EMAIL_PASSWORD


async def config_email_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda password y prueba conexión."""
    telegram_id = update.effective_user.id
    password = update.message.text.replace(' ', '')
    email = context.user_data['config_email']['gmail_user']
    
    # Borrar mensaje con password por seguridad
    try:
        await update.message.delete()
    except:
        pass
    
    await update.message.reply_text("🔄 Probando conexión...")
    
    result = test_gmail_connection(email, password)
    
    if result['success']:
        # Guardar en DB
        update_usuario(telegram_id, {
            'gmail_user': email,
            'gmail_app_password': password
        })
        
        await update.message.reply_text(
            "✅ *Gmail configurado correctamente*\n\n"
            f"📧 {email}\n\n"
            "Ahora tus tareas pueden enviar recordatorios por email.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Error de conexión*\n\n{result['error']}\n\n"
            "Verifica tus credenciales y vuelve a intentar con /config\\_email",
            parse_mode='Markdown'
        )
    
    context.user_data.pop('config_email', None)
    return ConversationHandler.END


# =============================================
# RECORDATORIOS RÁPIDOS (Lenguaje Natural)
# =============================================

def parse_quick_reminder(text: str) -> Optional[Dict]:
    """Parsea mensajes naturales para crear recordatorios rápidos."""
    text_lower = text.lower().strip()
    
    trigger_words = [
        'recordatorio', 'recordame', 'recuerdame', 'recordar',
        'avisame', 'avísame', 'aviso', 'alarma', 'alerta'
    ]
    
    if not any(word in text_lower for word in trigger_words):
        return None
    
    now = datetime.datetime.now(TZ)
    
    # Parsear fecha
    fecha = now.date()
    if 'mañana' in text_lower or 'manana' in text_lower:
        fecha = (now + datetime.timedelta(days=1)).date()
    elif 'pasado mañana' in text_lower:
        fecha = (now + datetime.timedelta(days=2)).date()
    else:
        match = re.search(r'(\d{1,2})[/-](\d{1,2})', text_lower)
        if match:
            try:
                day, month = int(match.group(1)), int(match.group(2))
                fecha = datetime.date(now.year, month, day)
                if fecha < now.date():
                    fecha = datetime.date(now.year + 1, month, day)
            except ValueError:
                pass
        else:
            for dia_nombre, dia_rel in DIAS_SEMANA.items():
                if dia_nombre in text_lower:
                    next_day = now + relativedelta(weekday=dia_rel(+1))
                    fecha = next_day.date()
                    break
    
    # Parsear hora
    hora = datetime.time(9, 0)
    time_patterns = [
        r'a\s+las?\s+(\d{1,2})[:h]?(\d{2})?\s*(?:hs?|horas?)?',
        r'(\d{1,2})[:h](\d{2})\s*(?:hs?|horas?)?',
        r'(\d{1,2})\s*(?:hs|horas?)',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            h = int(match.group(1))
            m = int(match.group(2)) if match.lastindex >= 2 and match.group(2) else 0
            try:
                hora = datetime.time(h, m)
            except ValueError:
                pass
            break
    
    # Extraer mensaje
    mensaje = text
    for word in trigger_words:
        mensaje = mensaje.lower().replace(word, '')
    mensaje = re.sub(r'\d{1,2}[/-]\d{1,2}', '', mensaje)
    mensaje = re.sub(r'a\s+las?\s+\d{1,2}[:h]?\d{0,2}\s*(?:hs?|horas?)?', '', mensaje)
    mensaje = re.sub(r'\d{1,2}\s*(?:hs|horas?)', '', mensaje)
    mensaje = re.sub(r'(?:mañana|manana|hoy|pasado)', '', mensaje)
    mensaje = re.sub(r'(?:para|el|la|de)\s+', ' ', mensaje)
    for dia in DIAS_SEMANA.keys():
        mensaje = mensaje.replace(dia, '')
    mensaje = ' '.join(mensaje.split()).strip()
    
    if not mensaje or len(mensaje) < 3:
        mensaje = text
    
    return {
        'fecha': fecha,
        'hora': hora,
        'mensaje': mensaje
    }


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa mensajes de texto para crear recordatorios rápidos."""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    telegram_id = update.effective_user.id
    
    parsed = parse_quick_reminder(text)
    
    if not parsed:
        await update.message.reply_text(
            "🤔 No entendí tu mensaje.\n\n"
            "Para recordatorios rápidos, escribe algo como:\n"
            "• _recordame mañana a las 10 llamar a Juan_\n\n"
            "O usa /ayuda para ver todos los comandos.",
            parse_mode='Markdown'
        )
        return
    
    fecha_vencimiento = TZ.localize(datetime.datetime.combine(parsed['fecha'], parsed['hora']))
    
    try:
        tarea_data = {
            'titulo': parsed['mensaje'][:100],
            'descripcion': parsed['mensaje'] if len(parsed['mensaje']) > 100 else None,
            'fecha_vencimiento': fecha_vencimiento.isoformat(),
            'estado': 'pendiente',
            'prioridad': 'media',
            'canal_notificacion': 'telegram'
        }
        
        tarea = create_tarea(telegram_id, tarea_data)
        
        # Crear recordatorio
        create_recordatorio_config(tarea['id'], {
            'dias_antes': 0,
            'hora': parsed['hora'].strftime('%H:%M:%S'),
            'canal': 'telegram'
        })
        
        await update.message.reply_text(
            f"✅ *Recordatorio creado*\n\n"
            f"📅 {parsed['fecha'].strftime('%d/%m/%Y')} a las {parsed['hora'].strftime('%H:%M')}\n"
            f"📝 _{parsed['mensaje']}_",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error creando recordatorio rápido: {e}")
        await update.message.reply_text("❌ Error creando recordatorio")


# =============================================
# MAIN
# =============================================

def main():
    """Punto de entrada principal."""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN no configurado")
        return
    
    logger.info("🚀 Iniciando CRM Bot...")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Comandos básicos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ayuda", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resumen", resumen_command))
    
    # Contactos
    app.add_handler(CommandHandler("contactos", contactos_command))
    app.add_handler(CommandHandler("buscar", buscar_contacto_command))
    
    contacto_conv = ConversationHandler(
        entry_points=[CommandHandler("nuevo_contacto", nuevo_contacto_start)],
        states={
            CONTACTO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_contacto_nombre)],
            CONTACTO_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_contacto_email),
                CallbackQueryHandler(nuevo_contacto_email, pattern="^skip_email$")
            ],
            CONTACTO_TELEFONO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_contacto_telefono),
                CallbackQueryHandler(nuevo_contacto_telefono, pattern="^skip_telefono$")
            ],
            CONTACTO_EMPRESA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_contacto_empresa),
                CallbackQueryHandler(nuevo_contacto_empresa, pattern="^skip_empresa$")
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancel_conversation)],
    )
    app.add_handler(contacto_conv)
    
    # Tareas
    app.add_handler(CommandHandler("tareas", tareas_command))
    app.add_handler(CommandHandler("hoy", tareas_hoy_command))
    app.add_handler(CommandHandler("completar", completar_tarea_command))
    
    tarea_conv = ConversationHandler(
        entry_points=[CommandHandler("nueva_tarea", nueva_tarea_start)],
        states={
            TAREA_TITULO: [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_tarea_titulo)],
            TAREA_CONTACTO: [CallbackQueryHandler(nueva_tarea_contacto, pattern="^contacto_")],
            TAREA_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_tarea_fecha)],
            TAREA_HORA: [CallbackQueryHandler(nueva_tarea_hora, pattern="^hora_")],
            TAREA_DESCRIPCION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_tarea_descripcion),
                CallbackQueryHandler(nueva_tarea_descripcion, pattern="^desc_none$")
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancel_conversation)],
    )
    app.add_handler(tarea_conv)
    
    # Proyectos
    app.add_handler(CommandHandler("proyectos", proyectos_command))
    
    proyecto_conv = ConversationHandler(
        entry_points=[CommandHandler("nuevo_proyecto", nuevo_proyecto_start)],
        states={
            PROYECTO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_proyecto_nombre)],
            PROYECTO_DESCRIPCION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_proyecto_descripcion),
                CallbackQueryHandler(nuevo_proyecto_descripcion, pattern="^skip_desc_proyecto$")
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancel_conversation)],
    )
    app.add_handler(proyecto_conv)
    
    # Configuración Email
    email_conv = ConversationHandler(
        entry_points=[CommandHandler("config_email", config_email_start)],
        states={
            CONFIG_EMAIL_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, config_email_user)],
            CONFIG_EMAIL_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, config_email_password)],
        },
        fallbacks=[CommandHandler("cancelar", cancel_conversation)],
    )
    app.add_handler(email_conv)
    
    # Mensajes generales (recordatorios rápidos)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Scheduler
    job_queue = app.job_queue
    job_queue.run_repeating(
        lambda ctx: process_pending_reminders(),
        interval=60,
        first=10
    )
    logger.info("⏰ Scheduler configurado")
    
    # Iniciar
    logger.info("✅ Bot iniciado. Esperando mensajes...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
