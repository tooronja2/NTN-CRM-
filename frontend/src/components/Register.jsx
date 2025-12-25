import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

function Register({ onSuccess }) {
    const [searchParams] = useSearchParams();
    const selectedPlan = searchParams.get('plan') || 'starter';

    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        nombre: '',
        email: '',
        telegramId: '',
        plan: selectedPlan
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (step === 1) {
            // Validar paso 1
            if (!formData.nombre || !formData.email) {
                setError('Por favor completa todos los campos');
                return;
            }
            setStep(2);
            return;
        }

        // Paso 2: Validar Telegram ID
        if (!formData.telegramId) {
            setError('Por favor ingresa tu ID de Telegram');
            return;
        }

        if (!/^\d+$/.test(formData.telegramId)) {
            setError('El ID de Telegram debe ser un número');
            return;
        }

        setLoading(true);

        try {
            // Por ahora solo simular registro
            // TODO: Conectar con API real
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Guardar telegram_id en localStorage
            localStorage.setItem('telegram_id', formData.telegramId);
            localStorage.setItem('user_name', formData.nombre);
            localStorage.setItem('user_email', formData.email);
            localStorage.setItem('user_plan', formData.plan);

            // Ir al paso de confirmación
            setStep(3);
        } catch (err) {
            setError('Error creando cuenta. Intenta de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const plans = {
        starter: { name: 'Starter', price: '$0/mes' },
        professional: { name: 'Professional', price: '$9/mes' },
        business: { name: 'Business', price: '$29/mes' }
    };

    return (
        <div className="landing-page">
            {/* Navbar */}
            <nav className="landing-nav">
                <div className="landing-nav-container">
                    <Link to="/" className="landing-logo">
                        📌 <span>CRM Follow-Up</span>
                    </Link>
                    <div className="landing-nav-links">
                        <Link to="/precios">Precios</Link>
                        <Link to="/login" className="btn btn-secondary btn-sm">Iniciar Sesión</Link>
                    </div>
                </div>
            </nav>

            {/* Register Form */}
            <section className="register-section">
                <div className="register-container">
                    <div className="register-card">
                        {/* Progress Steps */}
                        <div className="register-steps">
                            <div className={`register-step ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
                                <span className="step-num">1</span>
                                <span className="step-label">Tu info</span>
                            </div>
                            <div className="step-line"></div>
                            <div className={`register-step ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
                                <span className="step-num">2</span>
                                <span className="step-label">Telegram</span>
                            </div>
                            <div className="step-line"></div>
                            <div className={`register-step ${step >= 3 ? 'active' : ''}`}>
                                <span className="step-num">3</span>
                                <span className="step-label">¡Listo!</span>
                            </div>
                        </div>

                        {/* Step 1: Info básica */}
                        {step === 1 && (
                            <form onSubmit={handleSubmit}>
                                <h2>Crea tu cuenta gratis</h2>
                                <p className="register-subtitle">
                                    Plan seleccionado: <strong>{plans[formData.plan]?.name}</strong> ({plans[formData.plan]?.price})
                                </p>

                                <div className="form-group">
                                    <label className="form-label">Tu nombre</label>
                                    <input
                                        type="text"
                                        name="nombre"
                                        className="form-input"
                                        placeholder="Juan Pérez"
                                        value={formData.nombre}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        className="form-input"
                                        placeholder="juan@empresa.com"
                                        value={formData.email}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                {error && <div className="form-error">{error}</div>}

                                <button type="submit" className="btn btn-primary btn-block">
                                    Continuar →
                                </button>

                                <p className="register-login">
                                    ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
                                </p>
                            </form>
                        )}

                        {/* Step 2: Telegram ID */}
                        {step === 2 && (
                            <form onSubmit={handleSubmit}>
                                <h2>Conecta tu Telegram</h2>
                                <p className="register-subtitle">
                                    Necesitamos tu ID de Telegram para enviarte recordatorios y permitir gestión desde el chat.
                                </p>

                                <div className="telegram-instructions">
                                    <h4>¿Cómo obtener tu ID?</h4>
                                    <ol>
                                        <li>Abre Telegram</li>
                                        <li>Busca <strong>@userinfobot</strong></li>
                                        <li>Envíale cualquier mensaje</li>
                                        <li>Te responderá con tu ID (un número)</li>
                                    </ol>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Tu ID de Telegram</label>
                                    <input
                                        type="text"
                                        name="telegramId"
                                        className="form-input"
                                        placeholder="123456789"
                                        value={formData.telegramId}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                {error && <div className="form-error">{error}</div>}

                                <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                                    {loading ? 'Creando cuenta...' : 'Crear mi cuenta'}
                                </button>

                                <button
                                    type="button"
                                    className="btn btn-secondary btn-block"
                                    onClick={() => setStep(1)}
                                >
                                    ← Volver
                                </button>
                            </form>
                        )}

                        {/* Step 3: Confirmación */}
                        {step === 3 && (
                            <div className="register-success">
                                <div className="success-icon">🎉</div>
                                <h2>¡Cuenta creada!</h2>
                                <p>
                                    Hola <strong>{formData.nombre}</strong>, tu cuenta está lista.
                                </p>

                                <div className="next-steps">
                                    <h4>Próximos pasos:</h4>
                                    <div className="next-step-item">
                                        <span className="step-check">1</span>
                                        <div>
                                            <strong>Inicia el Bot de Telegram</strong>
                                            <p>Busca nuestro bot y envía <code>/start</code></p>
                                            <a href="https://t.me/tu_bot" target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                                                Abrir Bot →
                                            </a>
                                        </div>
                                    </div>
                                    <div className="next-step-item">
                                        <span className="step-check">2</span>
                                        <div>
                                            <strong>Accede al Panel</strong>
                                            <p>Gestiona contactos, tareas y proyectos desde la web.</p>
                                        </div>
                                    </div>
                                </div>

                                <Link to="/login" className="btn btn-primary btn-block">
                                    Ir al Panel →
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Side info */}
                    <div className="register-side">
                        <h3>Todo lo que obtienes:</h3>
                        <ul>
                            <li>✓ Bot de Telegram personal</li>
                            <li>✓ Dashboard web responsive</li>
                            <li>✓ Vista Kanban de tareas</li>
                            <li>✓ Recordatorios automáticos</li>
                            <li>✓ Gestión de contactos</li>
                            <li>✓ Sin límite de tiempo</li>
                        </ul>
                        <div className="register-testimonial">
                            <p>"Desde que uso CRM Follow-Up no pierdo ningún cliente. Los recordatorios automáticos son un game-changer."</p>
                            <span>— María G., Project Manager</span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Register;
