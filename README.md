# Bot de Recordatorios - Telegram + Supabase

Bot de Telegram simple para gestionar recordatorios. **Sin IA** - usa parsing determinístico.

## Características

- ✅ Crear recordatorios con lenguaje natural
- ✅ Recordatorios únicos o recurrentes (diario, semanal, mensual)
- ✅ Almacenamiento en Supabase
- ✅ Notificaciones automáticas

## Setup Rápido

### 1. Crear Bot de Telegram

1. Hablar con [@BotFather](https://t.me/botfather) en Telegram
2. Enviar `/newbot` y seguir instrucciones
3. Copiar el **token** del bot

### 2. Configurar Supabase

1. Ir a [supabase.com](https://supabase.com) y crear proyecto nuevo
2. Ir a **SQL Editor** → pegar contenido de `db_setup_simple.sql` → ejecutar
3. Ir a **Settings** → **API** → copiar:
   - **Project URL**
   - **anon public key**

### 3. Configurar Variables de Entorno

Crear archivo `.env`:

```env
TELEGRAM_TOKEN=tu_token_de_telegram
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJI...
```

### 4. Instalar y Ejecutar

```bash
pip install -r requirements.txt
python main_simple.py
```

## Uso del Bot

Escribe mensajes como:

| Mensaje | Resultado |
|---------|-----------|
| `recordame mañana a las 10 llamar a Juan` | Recordatorio mañana 10:00 |
| `genera recordatorio para el 25/12 a las 12hs que diga: reunión` | Recordatorio 25/12 12:00 |
| `avisame el lunes 9hs revisar emails` | Próximo lunes 09:00 |
| `recordatorio cada día a las 8 tomar vitaminas` | Diario 08:00 |

### Comandos

- `/start` - Bienvenida y ayuda
- `/mis_recordatorios` - Ver recordatorios activos
- `/ayuda` - Ver ayuda

## Despliegue en Railway

1. Crear proyecto en [railway.app](https://railway.app)
2. Conectar repositorio de GitHub
3. Agregar variables de entorno en Railway
4. Deploy automático

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `main_simple.py` | Bot principal |
| `db_setup_simple.sql` | Esquema de base de datos |
| `requirements.txt` | Dependencias Python |
| `.env.example` | Ejemplo de configuración |
