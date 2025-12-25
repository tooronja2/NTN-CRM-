# CRM Follow-Up - Checklist de Deploy 🚀

## Estado Actual

### ✅ Completado
- [x] Código frontend (Landing + Dashboard + Animaciones)
- [x] Código backend (API + Bot)
- [x] Tablas en Supabase
- [x] Deploy en Vercel
- [x] Variables de entorno en Vercel

### 🔴 Pendiente
- [ ] Crear Bot de Telegram
- [ ] Deploy en Railway (backend)
- [ ] Conectar Vercel ↔ Railway
- [ ] Configurar email SMTP (opcional)

---

## Paso a Paso

### 1️⃣ Crear Bot de Telegram (2 min)

1. Abre Telegram → busca **@BotFather**
2. Envía `/newbot`
3. Nombre: `CRM Follow-Up Bot`
4. Username: `crm_followup_TUNOMBRE_bot`
5. **Guarda el token**: `7824062301:AAGjz...`

---

### 2️⃣ Deploy en Railway (5 min)

1. Ve a [railway.app](https://railway.app) → Login con GitHub
2. **New Project** → **Deploy from GitHub repo**
3. Selecciona: `tooronja2/NTN-CRM-`

**Configuración:**

| Setting | Valor |
|---------|-------|
| Root Directory | `backend` |
| Start Command | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

**Variables de entorno:**

```env
TELEGRAM_TOKEN=<token del BotFather>
SUPABASE_URL=https://vybbamkbvbqssykyhodm.supabase.co
SUPABASE_KEY=<anon key de Supabase>
TIMEZONE=America/Argentina/Buenos_Aires
```

> 📝 La SUPABASE_KEY es la "anon public" que empieza con `eyJ...`  
> Ve a Supabase → Settings → API → anon key

4. Click **Deploy**
5. Espera que termine
6. Copia la URL generada (ej: `https://ntn-crm-production.up.railway.app`)

---

### 3️⃣ Conectar Vercel con Railway (1 min)

1. Vercel → tu proyecto → **Settings** → **Environment Variables**
2. Agregar:

| Variable | Valor |
|----------|-------|
| `VITE_API_URL` | `https://tu-url-de-railway.app` |

3. **Deployments** → Redeploy último deployment

---

### 4️⃣ Email SMTP (Opcional)

**Opciones gratuitas:**

| Servicio | Límite | Dificultad |
|----------|--------|------------|
| Gmail + App Password | 500/día | Fácil |
| Brevo (Sendinblue) | 300/día | Media |
| Resend | 100/día | Fácil |

**Para Gmail:**
1. Activar verificación en 2 pasos
2. Crear [App Password](https://myaccount.google.com/apppasswords)
3. Agregar en Railway:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=tu.email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_NAME=CRM Follow-Up
SMTP_USE_SSL=true
```

> ⚠️ Sin configurar SMTP, los recordatorios solo van por Telegram (funciona igual)

---

## Verificación Final

- [ ] Abrir la landing en Vercel → ¿Se ve bien?
- [ ] Registrarse con Telegram ID → ¿Funciona?
- [ ] Abrir el bot en Telegram → Enviar `/start`
- [ ] Crear un contacto desde la web
- [ ] Crear una tarea con recordatorio

---

## URLs del Proyecto

| Servicio | URL |
|----------|-----|
| Frontend (Vercel) | `https://tu-app.vercel.app` |
| Backend (Railway) | `https://tu-backend.railway.app` |
| Bot Telegram | `@tu_bot` |
| Supabase | `https://vybbamkbvbqssykyhodm.supabase.co` |
