"""
Bot de Recordatorios Simplificado (Sin IA)
==========================================
Parsea mensajes de texto natural para extraer recordatorios.
No requiere autenticación ni Gemini AI.
"""

import os
import re
import logging
import datetime
from typing import Optional, Tuple

import pytz
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables de Entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([TELEGRAM_TOKEN, SUPABASE_URL, SUPABASE_KEY]):
    logger.error("❌ Faltan variables de entorno. Revisa .env")
    exit(1)

# Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Conectado a Supabase")
except Exception as e:
    logger.error(f"❌ Error conectando a Supabase: {e}")
    exit(1)

# Timezone Argentina
TZ_AR = pytz.timezone('America/Argentina/Buenos_Aires')

# Mapeo de días de la semana
DIAS_SEMANA = {
    'lunes': MO, 'lun': MO,
    'martes': TU, 'mar': TU,
    'miércoles': WE, 'miercoles': WE, 'mie': WE,
    'jueves': TH, 'jue': TH,
    'viernes': FR, 'vie': FR,
    'sábado': SA, 'sabado': SA, 'sab': SA,
    'domingo': SU, 'dom': SU,
}

# --- PARSER DETERMINÍSTICO ---

def parse_reminder_message(text: str) -> Optional[dict]:
    """
    Parsea un mensaje de texto natural para extraer:
    - fecha (date)
    - hora (time)
    - mensaje del recordatorio (message)
    - patrón de repetición (repeat_pattern)
    
    Ejemplos soportados:
    - "genera recordatorio para el 25/12 a las 12hs que diga: llamar rodolfo"
    - "recordame mañana a las 10 pedir presupuesto"
    - "avísame el lunes 9hs reunión con Juan"
    - "recordatorio cada día a las 8 revisar emails"
    """
    text_lower = text.lower().strip()
    now = datetime.datetime.now(TZ_AR)
    
    # Verificar si es un mensaje de recordatorio
    trigger_words = [
        'recordatorio', 'recordame', 'recuerdame', 'recordar',
        'avisame', 'avísame', 'aviso', 'alarma', 'alerta',
        'genera recordatorio', 'crear recordatorio', 'nuevo recordatorio'
    ]
    
    is_reminder = any(word in text_lower for word in trigger_words)
    if not is_reminder:
        return None
    
    result = {
        'date': None,
        'time': None,
        'message': None,
        'repeat_pattern': None
    }
    
    # --- EXTRAER REPETICIÓN ---
    repeat_patterns = {
        r'cada\s+d[ií]a': 'daily',
        r'todos\s+los\s+d[ií]as': 'daily',
        r'diariamente': 'daily',
        r'cada\s+semana': 'weekly',
        r'semanalmente': 'weekly',
        r'cada\s+mes': 'monthly',
        r'mensualmente': 'monthly',
        r'cada\s+hora': 'hourly',
        r'cada\s+(\d+)\s+horas?': 'every_N_hours',
        r'cada\s+(\d+)\s+d[ií]as?': 'every_N_days',
    }
    
    for pattern, repeat_type in repeat_patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            if 'N' in repeat_type:
                n = int(match.group(1))
                result['repeat_pattern'] = repeat_type.replace('N', str(n))
            else:
                result['repeat_pattern'] = repeat_type
            break
    
    # --- EXTRAER FECHA ---
    date_found = None
    
    # Patrones de fecha específicos
    # Formato DD/MM o DD-MM o DD/MM/YYYY
    date_match = re.search(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?', text_lower)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(3)) if date_match.group(3) else now.year
        if year < 100:
            year += 2000
        try:
            date_found = datetime.date(year, month, day)
            # Si la fecha ya pasó este año, usar el próximo año
            if date_found < now.date() and not date_match.group(3):
                date_found = datetime.date(year + 1, month, day)
        except ValueError:
            pass
    
    # Palabras relativas
    if not date_found:
        if 'hoy' in text_lower:
            date_found = now.date()
        elif 'mañana' in text_lower or 'manana' in text_lower:
            date_found = (now + datetime.timedelta(days=1)).date()
        elif 'pasado mañana' in text_lower or 'pasado manana' in text_lower:
            date_found = (now + datetime.timedelta(days=2)).date()
        else:
            # Buscar día de la semana
            for dia_nombre, dia_rel in DIAS_SEMANA.items():
                if dia_nombre in text_lower:
                    # Próximo día de la semana
                    next_day = now + relativedelta(weekday=dia_rel(+1))
                    date_found = next_day.date()
                    break
    
    # Default: hoy si no se encontró fecha
    if not date_found:
        date_found = now.date()
    
    result['date'] = date_found
    
    # --- EXTRAER HORA ---
    time_found = None
    
    # Patrones de hora
    # "a las 12hs", "12:30", "a las 10", "9hs", "14 horas"
    time_patterns = [
        r'a\s+las?\s+(\d{1,2})[:h]?(\d{2})?\s*(?:hs?|horas?)?',
        r'(\d{1,2})[:h](\d{2})\s*(?:hs?|horas?)?',
        r'(\d{1,2})\s*(?:hs|horas?)',
        r'(\d{1,2})\s*(?:am|pm)',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            hour = int(match.group(1))
            # Verificar si existe grupo 2 y no es None
            minute = 0
            try:
                if match.lastindex and match.lastindex >= 2 and match.group(2):
                    minute = int(match.group(2))
            except (IndexError, TypeError):
                minute = 0
            
            # Ajustar AM/PM si está presente
            if 'pm' in text_lower and hour < 12:
                hour += 12
            elif 'am' in text_lower and hour == 12:
                hour = 0
                
            try:
                time_found = datetime.time(hour, minute)
            except ValueError:
                pass
            break
    
    # Default: hora actual + 1 hora si no se encontró
    if not time_found:
        future = now + datetime.timedelta(hours=1)
        time_found = future.time().replace(second=0, microsecond=0)
    
    result['time'] = time_found
    
    # --- EXTRAER MENSAJE ---
    # Buscar después de "que diga:", "para", "mensaje:", etc.
    message_patterns = [
        r'que\s+diga[:\s]+(.+)$',
        r'mensaje[:\s]+(.+)$',
        r'texto[:\s]+(.+)$',
        r'para[:\s]+(.+)$',
    ]
    
    message_text = None
    for pattern in message_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            message_text = match.group(1).strip()
            break
    
    # Si no hay patrón específico, extraer todo después de la hora/fecha
    if not message_text:
        # Remover las palabras de trigger y los datos de fecha/hora
        cleaned = text_lower
        for word in trigger_words:
            cleaned = cleaned.replace(word, '')
        
        # Remover patrones de fecha y hora ya procesados
        cleaned = re.sub(r'\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?', '', cleaned)
        cleaned = re.sub(r'a\s+las?\s+\d{1,2}[:h]?\d{0,2}\s*(?:hs?|horas?)?', '', cleaned)
        cleaned = re.sub(r'\d{1,2}\s*(?:hs|horas?)', '', cleaned)
        cleaned = re.sub(r'(?:hoy|mañana|manana|pasado mañana)', '', cleaned)
        cleaned = re.sub(r'(?:para|el|la|los|las|del|de)\s+', ' ', cleaned)
        
        # Remover días de la semana
        for dia in DIAS_SEMANA.keys():
            cleaned = cleaned.replace(dia, '')
        
        # Limpiar espacios extra
        message_text = ' '.join(cleaned.split()).strip()
    
    # Si aún no hay mensaje, usar el texto original limpio
    if not message_text or len(message_text) < 3:
        message_text = text
    
    result['message'] = message_text
    
    return result


def calculate_next_occurrence(current_time: datetime.datetime, pattern: str, now: datetime.datetime) -> Optional[datetime.datetime]:
    """Calcula la próxima ocurrencia basada en el patrón de repetición."""
    if not pattern:
        return None
    
    if pattern == 'daily':
        return current_time + datetime.timedelta(days=1)
    elif pattern == 'weekly':
        return current_time + datetime.timedelta(weeks=1)
    elif pattern == 'monthly':
        return current_time + relativedelta(months=1)
    elif pattern == 'hourly':
        return current_time + datetime.timedelta(hours=1)
    elif pattern.startswith('every_'):
        match = re.match(r'every_(\d+)_(hours?|days?)', pattern)
        if match:
            n = int(match.group(1))
            unit = match.group(2)
            if 'hour' in unit:
                return current_time + datetime.timedelta(hours=n)
            elif 'day' in unit:
                return current_time + datetime.timedelta(days=n)
    
    return None


# --- HANDLERS DE TELEGRAM ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida."""
    welcome_text = """
👋 **¡Hola! Soy tu Bot de Recordatorios**

Puedo ayudarte a crear recordatorios de forma simple. Solo escríbeme mensajes como:

📝 **Ejemplos:**
• `recordame mañana a las 10 llamar al cliente`
• `genera recordatorio para el 25/12 a las 12hs que diga: reunión importante`
• `avisame el lunes 9hs revisar emails`
• `recordatorio cada día a las 8 tomar vitaminas`

📖 **Comandos:**
• `/mis_recordatorios` - Ver tus recordatorios activos
• `/ayuda` - Ver esta ayuda

¡Simplemente escríbeme y te ayudo! ⏰
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda - Mostrar ayuda."""
    await start_command(update, context)


async def list_reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /mis_recordatorios - Listar recordatorios activos."""
    telegram_id = update.effective_user.id
    
    try:
        resp = supabase.table('reminders').select('*')\
            .eq('telegram_id', telegram_id)\
            .eq('is_active', True)\
            .order('trigger_time')\
            .limit(20)\
            .execute()
        
        if not resp.data:
            await update.message.reply_text("📭 No tienes recordatorios activos.")
            return
        
        lines = ["📋 **Tus recordatorios activos:**\n"]
        for i, r in enumerate(resp.data, 1):
            trigger_str = r['trigger_time']
            try:
                dt = datetime.datetime.fromisoformat(trigger_str.replace('Z', '+00:00'))
                dt_ar = dt.astimezone(TZ_AR)
                formatted = dt_ar.strftime('%d/%m/%Y %H:%M')
            except:
                formatted = trigger_str
            
            repeat_icon = "🔁" if r.get('repeat_pattern') else "⏰"
            lines.append(f"{i}. {repeat_icon} **{formatted}**\n   _{r['message']}_\n")
        
        await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error listando recordatorios: {e}")
        await update.message.reply_text("❌ Error al obtener recordatorios.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa mensajes de texto para crear recordatorios."""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    telegram_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    logger.info(f"📩 Mensaje de {telegram_id}: {text}")
    
    # Intentar parsear como recordatorio
    parsed = parse_reminder_message(text)
    
    if not parsed:
        await update.message.reply_text(
            "🤔 No entendí tu mensaje como un recordatorio.\n\n"
            "Prueba con algo como:\n"
            "• _recordame mañana a las 10 llamar a Juan_\n"
            "• _genera recordatorio para el 25/12 a las 15hs que diga: reunión_",
            parse_mode='Markdown'
        )
        return
    
    # Construir datetime del trigger
    try:
        trigger_naive = datetime.datetime.combine(parsed['date'], parsed['time'])
        trigger_dt = TZ_AR.localize(trigger_naive)
        
        now = datetime.datetime.now(TZ_AR)
        
        # Si es pasado y no hay repetición, avisar
        if trigger_dt < now and not parsed['repeat_pattern']:
            # Intentar mañana a la misma hora
            trigger_dt = trigger_dt + datetime.timedelta(days=1)
            logger.info(f"Fecha pasada, ajustando a: {trigger_dt}")
        
        # Guardar en DB
        reminder_data = {
            'telegram_id': telegram_id,
            'chat_id': chat_id,
            'message': parsed['message'],
            'trigger_time': trigger_dt.isoformat(),
            'repeat_pattern': parsed['repeat_pattern'],
            'is_active': True
        }
        
        resp = supabase.table('reminders').insert(reminder_data).execute()
        
        if resp.data:
            # Mensaje de confirmación
            date_str = trigger_dt.strftime('%d/%m/%Y')
            time_str = trigger_dt.strftime('%H:%M')
            
            repeat_text = ""
            if parsed['repeat_pattern']:
                repeat_map = {
                    'daily': 'cada día',
                    'weekly': 'cada semana',
                    'monthly': 'cada mes',
                    'hourly': 'cada hora',
                }
                repeat_text = f"\n🔁 Repetición: **{repeat_map.get(parsed['repeat_pattern'], parsed['repeat_pattern'])}**"
            
            confirmation = (
                f"✅ **Recordatorio creado**\n\n"
                f"📅 Fecha: **{date_str}**\n"
                f"🕐 Hora: **{time_str}**\n"
                f"📝 Mensaje: _{parsed['message']}_"
                f"{repeat_text}"
            )
            
            await update.message.reply_text(confirmation, parse_mode='Markdown')
            logger.info(f"✅ Recordatorio creado: {reminder_data}")
        else:
            await update.message.reply_text("❌ Error guardando el recordatorio.")
            
    except Exception as e:
        logger.error(f"Error creando recordatorio: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


# --- CRON JOB PARA ENVIAR RECORDATORIOS ---

async def send_reminder_notification(application, reminder: dict):
    """Envía la notificación de un recordatorio."""
    try:
        message = f"⏰ **RECORDATORIO**\n\n{reminder['message']}"
        
        sent = await application.bot.send_message(
            chat_id=reminder['chat_id'],
            text=message,
            parse_mode='Markdown'
        )
        
        # Actualizar last_message_id
        supabase.table('reminders').update({
            'last_message_id': sent.message_id
        }).eq('id', reminder['id']).execute()
        
        logger.info(f"📤 Recordatorio {reminder['id']} enviado")
        
        # Manejar repetición o desactivar
        if reminder.get('repeat_pattern'):
            trigger_str = reminder['trigger_time']
            try:
                current = datetime.datetime.fromisoformat(trigger_str.replace('Z', '+00:00'))
            except:
                current = datetime.datetime.strptime(trigger_str, '%Y-%m-%d %H:%M:%S')
            
            if current.tzinfo is None:
                current = TZ_AR.localize(current)
            
            now = datetime.datetime.now(TZ_AR)
            next_time = calculate_next_occurrence(current, reminder['repeat_pattern'], now)
            
            if next_time:
                supabase.table('reminders').update({
                    'trigger_time': next_time.isoformat()
                }).eq('id', reminder['id']).execute()
                logger.info(f"🔁 Reprogramado para {next_time}")
            else:
                supabase.table('reminders').update({'is_active': False}).eq('id', reminder['id']).execute()
        else:
            supabase.table('reminders').update({'is_active': False}).eq('id', reminder['id']).execute()
            
    except Exception as e:
        logger.error(f"❌ Error enviando recordatorio {reminder['id']}: {e}")


async def check_reminders_job(context: ContextTypes.DEFAULT_TYPE):
    """Job que revisa y envía recordatorios pendientes."""
    try:
        now = datetime.datetime.now(TZ_AR)
        logger.info(f"🔍 Checking reminders at {now.isoformat()}")
        
        # Traer todos los activos
        resp = supabase.table('reminders').select('*').eq('is_active', True).execute()
        
        if not resp.data:
            return
        
        for r in resp.data:
            try:
                trigger_str = r['trigger_time']
                try:
                    trigger_dt = datetime.datetime.fromisoformat(trigger_str.replace('Z', '+00:00'))
                except ValueError:
                    trigger_dt = datetime.datetime.strptime(trigger_str, '%Y-%m-%d %H:%M:%S')
                
                if trigger_dt.tzinfo is None:
                    trigger_dt = TZ_AR.localize(trigger_dt)
                else:
                    trigger_dt = trigger_dt.astimezone(TZ_AR)
                
                # Si ya pasó la hora, enviar
                if trigger_dt <= now:
                    await send_reminder_notification(context.application, r)
                    
            except Exception as parse_err:
                logger.error(f"Error parseando recordatorio {r['id']}: {parse_err}")
                
    except Exception as e:
        logger.error(f"❌ Error en check_reminders_job: {e}")


# --- MAIN ---

def main():
    """Punto de entrada principal."""
    logger.info("🚀 Iniciando Bot de Recordatorios...")
    
    # Crear aplicación
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Registrar handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ayuda", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mis_recordatorios", list_reminders_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Job para revisar recordatorios cada minuto
    job_queue = app.job_queue
    job_queue.run_repeating(check_reminders_job, interval=60, first=10)
    logger.info("⏰ Job de recordatorios configurado (cada 60s)")
    
    # Iniciar bot
    logger.info("✅ Bot iniciado. Esperando mensajes...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
