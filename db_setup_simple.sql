-- =============================================
-- ESQUEMA SIMPLIFICADO: Solo Recordatorios
-- =============================================

-- Tabla de recordatorios (única tabla necesaria)
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    trigger_time TIMESTAMP WITH TIME ZONE NOT NULL,
    repeat_pattern VARCHAR(50), -- 'daily', 'weekly', 'monthly', NULL para único
    is_active BOOLEAN DEFAULT TRUE,
    last_message_id BIGINT, -- Para contexto de respuestas
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para búsqueda eficiente de recordatorios pendientes
CREATE INDEX IF NOT EXISTS idx_reminders_trigger ON reminders (trigger_time, is_active);
CREATE INDEX IF NOT EXISTS idx_reminders_telegram ON reminders (telegram_id, is_active);

-- =============================================
-- IMPORTANTE: Ejecutar este SQL en Supabase
-- 1. Ir a supabase.com → Tu proyecto → SQL Editor
-- 2. Pegar este contenido y ejecutar
-- =============================================
