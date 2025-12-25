import { useState } from 'react';
import { setTelegramId } from '../api/client';

function Login({ onLogin }) {
    const [telegramId, setTelegramIdState] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!telegramId.trim()) {
            setError('Por favor ingresa tu ID de Telegram');
            return;
        }

        // Validar que sea un número
        if (!/^\d+$/.test(telegramId.trim())) {
            setError('El ID de Telegram debe ser un número');
            return;
        }

        setLoading(true);

        try {
            // Guardar el telegram_id
            setTelegramId(telegramId.trim());

            // Intentar obtener datos del dashboard para verificar conexión
            const response = await fetch('/api/health');
            if (response.ok) {
                onLogin();
            } else {
                throw new Error('Error de conexión');
            }
        } catch (err) {
            // Aún así intentamos, la API puede crear el usuario
            onLogin();
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-logo">📌 CRM Follow-Up</div>
                <p className="login-subtitle">Automatización de seguimientos</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Tu ID de Telegram</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="Ej: 123456789"
                            value={telegramId}
                            onChange={(e) => setTelegramIdState(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div style={{ color: 'var(--error)', marginBottom: '16px', fontSize: '0.875rem' }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%' }}
                        disabled={loading}
                    >
                        {loading ? <span className="spinner" /> : 'Entrar'}
                    </button>
                </form>

                <div style={{ marginTop: '24px', padding: '16px', background: 'var(--gray-50)', borderRadius: '8px' }}>
                    <p style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '8px' }}>
                        <strong>¿Cómo obtener tu ID?</strong>
                    </p>
                    <ol style={{ fontSize: '0.8rem', color: 'var(--gray-500)', paddingLeft: '16px', lineHeight: 1.6 }}>
                        <li>Abre Telegram</li>
                        <li>Busca @userinfobot</li>
                        <li>Envíale cualquier mensaje</li>
                        <li>Te responderá con tu ID</li>
                    </ol>
                </div>

                <p style={{ marginTop: '24px', fontSize: '0.75rem', color: 'var(--gray-400)' }}>
                    Primero debes iniciar el bot con /start en Telegram
                </p>
            </div>
        </div>
    );
}

export default Login;
