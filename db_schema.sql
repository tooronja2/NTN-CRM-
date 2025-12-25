-- =============================================
-- CRM FOLLOW-UP AUTOMATION - ESQUEMA COMPLETO
-- =============================================
-- Ejecutar en Supabase: SQL Editor -> Pegar todo -> Run

-- =============================================
-- 1. TABLA DE USUARIOS (Project Managers)
-- =============================================
CREATE TABLE IF NOT EXISTS usuarios (
    telegram_id BIGINT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),               -- Email del usuario (para Reply-To y CC)
    timezone VARCHAR(50) DEFAULT 'America/Argentina/Buenos_Aires',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 2. TABLA DE CONTACTOS
-- =============================================
CREATE TABLE IF NOT EXISTS contactos (
    id SERIAL PRIMARY KEY,
    usuario_telegram_id BIGINT NOT NULL REFERENCES usuarios(telegram_id) ON DELETE CASCADE,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(50),
    telegram_id BIGINT,               -- Si el contacto tiene Telegram
    empresa VARCHAR(255),
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contactos_usuario ON contactos(usuario_telegram_id);
CREATE INDEX IF NOT EXISTS idx_contactos_nombre ON contactos(nombre);

-- =============================================
-- 3. TABLA DE PROYECTOS
-- =============================================
CREATE TABLE IF NOT EXISTS proyectos (
    id SERIAL PRIMARY KEY,
    usuario_telegram_id BIGINT NOT NULL REFERENCES usuarios(telegram_id) ON DELETE CASCADE,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    contacto_id INT REFERENCES contactos(id) ON DELETE SET NULL,
    estado VARCHAR(50) DEFAULT 'activo', -- 'activo', 'pausado', 'completado', 'cancelado'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proyectos_usuario ON proyectos(usuario_telegram_id);
CREATE INDEX IF NOT EXISTS idx_proyectos_estado ON proyectos(estado);

-- =============================================
-- 4. TABLA DE TAREAS
-- =============================================
CREATE TABLE IF NOT EXISTS tareas (
    id SERIAL PRIMARY KEY,
    usuario_telegram_id BIGINT NOT NULL REFERENCES usuarios(telegram_id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    contacto_id INT REFERENCES contactos(id) ON DELETE SET NULL,
    proyecto_id INT REFERENCES proyectos(id) ON DELETE SET NULL,
    fecha_vencimiento TIMESTAMP WITH TIME ZONE,
    estado VARCHAR(50) DEFAULT 'pendiente', -- 'pendiente', 'en_seguimiento', 'esperando_respuesta', 'completado'
    prioridad VARCHAR(20) DEFAULT 'media',  -- 'baja', 'media', 'alta', 'urgente'
    frecuencia_repeticion VARCHAR(50),      -- NULL, 'daily', 'weekly', 'monthly', 'every_N_days'
    canal_notificacion VARCHAR(50) DEFAULT 'telegram', -- 'telegram', 'email', 'ambos'
    plantilla_id INT,                       -- Referencia a plantilla (se agrega después)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tareas_usuario ON tareas(usuario_telegram_id);
CREATE INDEX IF NOT EXISTS idx_tareas_estado ON tareas(estado);
CREATE INDEX IF NOT EXISTS idx_tareas_vencimiento ON tareas(fecha_vencimiento);
CREATE INDEX IF NOT EXISTS idx_tareas_contacto ON tareas(contacto_id);

-- =============================================
-- 5. TABLA DE RECORDATORIOS CONFIGURADOS
-- (Múltiples recordatorios por tarea)
-- =============================================
CREATE TABLE IF NOT EXISTS recordatorios_config (
    id SERIAL PRIMARY KEY,
    tarea_id INT NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    dias_antes INT NOT NULL DEFAULT 0,        -- 0 = el mismo día, 1 = 1 día antes, etc.
    hora TIME NOT NULL DEFAULT '09:00',       -- Hora del recordatorio
    canal VARCHAR(50) DEFAULT 'telegram',     -- 'telegram', 'email', 'ambos'
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recordatorios_config_tarea ON recordatorios_config(tarea_id);

-- =============================================
-- 6. TABLA DE RECORDATORIOS ENVIADOS (LOG)
-- =============================================
CREATE TABLE IF NOT EXISTS recordatorios_enviados (
    id SERIAL PRIMARY KEY,
    tarea_id INT REFERENCES tareas(id) ON DELETE SET NULL,
    recordatorio_config_id INT REFERENCES recordatorios_config(id) ON DELETE SET NULL,
    fecha_envio TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    canal VARCHAR(50) NOT NULL,               -- 'telegram', 'email'
    estado VARCHAR(50) DEFAULT 'enviado',     -- 'enviado', 'fallido', 'pendiente'
    mensaje TEXT,
    error_mensaje TEXT                        -- Si falló, guardar error
);

CREATE INDEX IF NOT EXISTS idx_recordatorios_enviados_tarea ON recordatorios_enviados(tarea_id);
CREATE INDEX IF NOT EXISTS idx_recordatorios_enviados_fecha ON recordatorios_enviados(fecha_envio);

-- =============================================
-- 7. TABLA DE PLANTILLAS
-- =============================================
CREATE TABLE IF NOT EXISTS plantillas (
    id SERIAL PRIMARY KEY,
    usuario_telegram_id BIGINT NOT NULL REFERENCES usuarios(telegram_id) ON DELETE CASCADE,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,                -- 'email', 'telegram'
    asunto VARCHAR(255),                      -- Solo para email
    mensaje TEXT NOT NULL,                    -- Contenido con variables: {{nombre}}, {{proyecto}}, {{fecha}}
    es_default BOOLEAN DEFAULT FALSE,         -- Plantilla por defecto
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plantillas_usuario ON plantillas(usuario_telegram_id);
CREATE INDEX IF NOT EXISTS idx_plantillas_tipo ON plantillas(tipo);

-- Agregar FK de plantilla a tareas
ALTER TABLE tareas 
ADD CONSTRAINT fk_tareas_plantilla 
FOREIGN KEY (plantilla_id) REFERENCES plantillas(id) ON DELETE SET NULL;

-- =============================================
-- 8. TABLA DE HISTORIAL DE INTERACCIONES
-- =============================================
CREATE TABLE IF NOT EXISTS historial_interacciones (
    id SERIAL PRIMARY KEY,
    usuario_telegram_id BIGINT NOT NULL REFERENCES usuarios(telegram_id) ON DELETE CASCADE,
    contacto_id INT REFERENCES contactos(id) ON DELETE CASCADE,
    tarea_id INT REFERENCES tareas(id) ON DELETE SET NULL,
    tipo VARCHAR(50) NOT NULL,                -- 'email_enviado', 'telegram_enviado', 'tarea_completada', 'nota_agregada'
    descripcion TEXT,
    metadata JSONB,                           -- Datos adicionales (email subject, etc)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historial_contacto ON historial_interacciones(contacto_id);
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_interacciones(created_at);

-- =============================================
-- 9. MIGRACIÓN: Conservar tabla reminders existente
-- =============================================
-- La tabla 'reminders' existente se mantiene como backup
-- Los nuevos recordatorios usarán el nuevo esquema

-- =============================================
-- 10. FUNCIONES AUXILIARES
-- =============================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
DROP TRIGGER IF EXISTS update_contactos_updated_at ON contactos;
CREATE TRIGGER update_contactos_updated_at
    BEFORE UPDATE ON contactos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_proyectos_updated_at ON proyectos;
CREATE TRIGGER update_proyectos_updated_at
    BEFORE UPDATE ON proyectos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tareas_updated_at ON tareas;
CREATE TRIGGER update_tareas_updated_at
    BEFORE UPDATE ON tareas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 11. PLANTILLAS POR DEFECTO (se insertan después de crear usuario)
-- =============================================
-- Las plantillas por defecto se crean cuando el usuario se registra

-- =============================================
-- LISTO! Ejecutar todo este SQL en Supabase
-- =============================================
