import { Link } from 'react-router-dom';

function Landing() {
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
                        <Link to="/registro" className="btn btn-primary btn-sm">Comenzar Gratis</Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <div className="hero-badge">🚀 La herramienta que necesitas</div>
                    <h1 className="hero-title">
                        Automatiza tus <span className="gradient-text">Follow-Ups</span> y nunca pierdas un cliente
                    </h1>
                    <p className="hero-subtitle">
                        El CRM diseñado para Project Managers que quieren mantener el control de sus contactos,
                        tareas y recordatorios. Gestiona desde la web o Telegram.
                    </p>
                    <div className="hero-cta">
                        <Link to="/registro" className="btn btn-primary btn-lg">
                            Comenzar Gratis →
                        </Link>
                        <Link to="/precios" className="btn btn-secondary btn-lg">
                            Ver Planes
                        </Link>
                    </div>
                    <div className="hero-trust">
                        <span>✓ Sin tarjeta de crédito</span>
                        <span>✓ Setup en 2 minutos</span>
                        <span>✓ Soporte por Telegram</span>
                    </div>
                </div>
                <div className="hero-image">
                    <div className="hero-mockup">
                        <div className="mockup-header">
                            <div className="mockup-dots">
                                <span></span><span></span><span></span>
                            </div>
                            <span>Dashboard</span>
                        </div>
                        <div className="mockup-content">
                            <div className="mockup-stat">📊 12 tareas pendientes</div>
                            <div className="mockup-stat">👥 45 contactos</div>
                            <div className="mockup-stat">🔔 3 recordatorios hoy</div>
                            <div className="mockup-kanban">
                                <div className="mock-col">🔴 Pendiente</div>
                                <div className="mock-col">🟡 En curso</div>
                                <div className="mock-col">🟢 Completado</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section" id="features">
                <div className="section-container">
                    <div className="section-header">
                        <h2>Todo lo que necesitas para gestionar tus follow-ups</h2>
                        <p>Funcionalidades diseñadas para project managers que no quieren perder oportunidades</p>
                    </div>
                    <div className="features-grid">
                        <div className="feature-card">
                            <div className="feature-icon">📋</div>
                            <h3>Vista Kanban</h3>
                            <p>Visualiza todas tus tareas en un tablero drag & drop. Mueve tareas entre estados con un click.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">📱</div>
                            <h3>Bot de Telegram</h3>
                            <p>Gestiona todo desde Telegram. Crea tareas, contactos y recibe recordatorios sin abrir la web.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">📧</div>
                            <h3>Emails Automáticos</h3>
                            <p>Envía recordatorios automáticos a tus contactos. Plantillas personalizables con variables.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">⏰</div>
                            <h3>Recordatorios Múltiples</h3>
                            <p>Configura varios recordatorios por tarea: 3 días antes, 1 día antes, el mismo día.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">👥</div>
                            <h3>Gestión de Contactos</h3>
                            <p>Centraliza toda la información de tus clientes con historial de interacciones.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">🗂</div>
                            <h3>Proyectos</h3>
                            <p>Agrupa tareas por proyecto. Mantén organizados todos los seguimientos de cada cliente.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="how-section">
                <div className="section-container">
                    <div className="section-header">
                        <h2>¿Cómo funciona?</h2>
                        <p>Comienza en menos de 2 minutos</p>
                    </div>
                    <div className="steps-grid">
                        <div className="step-card">
                            <div className="step-number">1</div>
                            <h3>Regístrate gratis</h3>
                            <p>Solo necesitas tu Telegram ID para comenzar</p>
                        </div>
                        <div className="step-arrow">→</div>
                        <div className="step-card">
                            <div className="step-number">2</div>
                            <h3>Conecta el Bot</h3>
                            <p>Inicia nuestro bot en Telegram con /start</p>
                        </div>
                        <div className="step-arrow">→</div>
                        <div className="step-card">
                            <div className="step-number">3</div>
                            <h3>Crea tu primer contacto</h3>
                            <p>Agrega contactos y tareas desde la web o el bot</p>
                        </div>
                        <div className="step-arrow">→</div>
                        <div className="step-card">
                            <div className="step-number">4</div>
                            <h3>Recibe recordatorios</h3>
                            <p>El sistema te avisa automáticamente por Telegram y email</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="section-container">
                    <h2>¿Listo para no perder más clientes?</h2>
                    <p>Únete a cientos de project managers que ya automatizan sus follow-ups</p>
                    <Link to="/registro" className="btn btn-primary btn-lg">
                        Comenzar Gratis Ahora →
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="footer-container">
                    <div className="footer-brand">
                        <div className="landing-logo">📌 CRM Follow-Up</div>
                        <p>Automatiza tus seguimientos y cierra más deals.</p>
                    </div>
                    <div className="footer-links">
                        <div className="footer-col">
                            <h4>Producto</h4>
                            <Link to="/precios">Precios</Link>
                            <a href="#features">Funcionalidades</a>
                        </div>
                        <div className="footer-col">
                            <h4>Cuenta</h4>
                            <Link to="/login">Iniciar Sesión</Link>
                            <Link to="/registro">Registrarse</Link>
                        </div>
                        <div className="footer-col">
                            <h4>Soporte</h4>
                            <a href="https://t.me/tubot" target="_blank" rel="noopener noreferrer">Telegram</a>
                        </div>
                    </div>
                </div>
                <div className="footer-bottom">
                    <p>© 2024 CRM Follow-Up. Todos los derechos reservados.</p>
                </div>
            </footer>
        </div>
    );
}

export default Landing;
