# CRM Follow-Up Automation 📌

Sistema CRM simple enfocado en **automatización de follow-up** para project managers.

## ✨ Características

- **📋 Gestión de Tareas** - Vista Kanban drag & drop + lista
- **👥 Contactos** - Base de datos de clientes con historial
- **🗂 Proyectos** - Organiza tareas por proyecto
- **📝 Plantillas** - Mensajes personalizados con variables dinámicas
- **⏰ Recordatorios automáticos** - Por Telegram y Email
- **📱 Bot de Telegram** - Gestión completa desde el chat
- **🌐 Web responsive** - Funciona en móvil y PC

## 🏗 Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │    Backend      │     │   Servicios     │
│   React + Vite  │────▶│    FastAPI      │────▶│   Supabase      │
│                 │     │                 │     │   SMTP          │
└─────────────────┘     │    Bot          │     │   Telegram API  │
                        │    Telegram     │     └─────────────────┘
                        └─────────────────┘
```

## 🚀 Instalación

### Requisitos previos

- Python 3.10+
- Node.js 18+
- Cuenta en [Supabase](https://supabase.com)
- Bot de Telegram (crear con [@BotFather](https://t.me/botfather))
- Servidor SMTP (tu dominio o Gmail)

### Paso 1: Configurar Base de Datos (Supabase)

1. Ir a [supabase.com](https://supabase.com) → Crear nuevo proyecto
2. Ir a **SQL Editor** → Pegar contenido de `db_schema.sql` → Ejecutar
3. Ir a **Settings** → **API** → Copiar:
   - `Project URL` → para `SUPABASE_URL`
   - `anon public key` → para `SUPABASE_KEY`

### Paso 2: Crear Bot de Telegram

1. Abrir [@BotFather](https://t.me/botfather) en Telegram
2. Enviar `/newbot` y seguir instrucciones
3. Copiar el **token** del bot

### Paso 3: Configurar Variables de Entorno

Crear archivo `backend/.env`:

```env
# Telegram Bot
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJI...

# SMTP Centralizado (tu dominio)
SMTP_HOST=smtp.tudominio.com
SMTP_PORT=465
SMTP_USER=noreply@tudominio.com
SMTP_PASSWORD=tu_password
SMTP_FROM_NAME=CRM Follow-Up
SMTP_USE_SSL=true

# Opcional
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
TIMEZONE=America/Argentina/Buenos_Aires
```

> 💡 **Nota sobre SMTP**: Los emails salen de tu dominio centralizado. El email del usuario va en **Reply-To** y **CC** para que reciba las respuestas de sus contactos.

### Paso 4: Instalar Backend

```bash
cd backend
pip install -r requirements.txt
```

### Paso 5: Instalar Frontend

```bash
cd frontend
npm install
```

---

## 🏃 Ejecución

### Desarrollo Local

**Terminal 1 - Backend API:**
```bash
cd backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Bot Telegram:**
```bash
cd backend
python -m bot.telegram_bot
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

Acceder a:
- **Web:** http://localhost:5173
- **API:** http://localhost:8000/docs

---

## 📱 Uso del Bot de Telegram

### Comandos principales

| Comando | Descripción |
|---------|-------------|
| `/start` | Registrarse y ver ayuda |
| `/contactos` | Listar contactos |
| `/nuevo_contacto` | Crear contacto (wizard) |
| `/buscar [nombre]` | Buscar contacto |
| `/tareas` | Ver tareas pendientes |
| `/hoy` | Tareas de hoy |
| `/nueva_tarea` | Crear tarea (wizard) |
| `/completar [id]` | Marcar tarea completada |
| `/proyectos` | Ver proyectos |
| `/resumen` | Dashboard rápido |

### Recordatorios rápidos

Escribe mensajes naturales:

- `recordame mañana a las 10 llamar a Juan`
- `avisame el lunes 9hs revisar presupuesto`
- `recordatorio para el 25/12 a las 12hs reunión importante`

---

## 🌐 Uso de la Web

1. Abrir http://localhost:5173
2. Ingresar tu **ID de Telegram** (obtener con @userinfobot)
3. Navegar por las secciones:
   - **Dashboard** - Vista general + Kanban
   - **Contactos** - CRUD de contactos
   - **Tareas** - Kanban drag & drop
   - **Proyectos** - Gestión de proyectos
   - **Plantillas** - Editor de templates

---

## 📧 Configuración de Emails

### Opción A: Tu propio dominio (Recomendado para SaaS)

Configura un servidor SMTP con tu dominio:
```env
SMTP_HOST=smtp.tudominio.com
SMTP_PORT=465
SMTP_USER=noreply@tudominio.com
SMTP_PASSWORD=password
```

### Opción B: Gmail (para testing)

1. Activar verificación en 2 pasos en Google
2. Crear [App Password](https://myaccount.google.com/apppasswords)
3. Configurar:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=tu.email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

---

## 📂 Estructura del Proyecto

```
NTN-CRM-/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/              # Endpoints
│   │   ├── models/              # Schemas Pydantic
│   │   └── services/            # Lógica de negocio
│   ├── bot/
│   │   └── telegram_bot.py      # Bot completo
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/          # React components
│   │   └── api/                 # API client
│   ├── package.json
│   └── vite.config.js
├── db_schema.sql                # Esquema de BD
└── README.md
```

---

## 🚀 Despliegue en Producción

### Backend (Railway/Render)

1. Crear proyecto en Railway/Render
2. Conectar repositorio
3. Configurar variables de entorno
4. Deploy automático

### Frontend (Vercel)

1. Crear proyecto en Vercel
2. Conectar repositorio → carpeta `frontend`
3. Build: `npm run build`
4. Deploy automático

### Cron Jobs

Para recordatorios automáticos en producción, el scheduler ya corre dentro de la API. Alternativamente, puedes usar:
- **Railway Cron**: Llamar `POST /api/trigger-reminders` cada minuto
- **Vercel Cron**: Configurar en `vercel.json`

---

## 🔧 Variables de Plantillas

Disponibles para usar en plantillas:

| Variable | Descripción |
|----------|-------------|
| `{{titulo}}` | Título de la tarea |
| `{{descripcion}}` | Descripción |
| `{{fecha_vencimiento}}` | Fecha límite |
| `{{contacto_nombre}}` | Nombre del contacto |
| `{{contacto_email}}` | Email del contacto |
| `{{contacto_empresa}}` | Empresa |
| `{{prioridad}}` | Prioridad de la tarea |

**Ejemplo de plantilla:**
```
Hola {{contacto_nombre}},

Te recuerdo sobre: {{titulo}}
Fecha: {{fecha_vencimiento}}

{{descripcion}}

Saludos
```

---

## 📄 Licencia

MIT
