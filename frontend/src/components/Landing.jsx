import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

// Hook para detectar si un elemento está visible
function useInView(options = {}) {
    const ref = useRef(null);
    const [isInView, setIsInView] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting) {
                setIsInView(true);
                // Una vez visible, dejar de observar
                if (ref.current) observer.unobserve(ref.current);
            }
        }, { threshold: 0.1, ...options });

        if (ref.current) observer.observe(ref.current);

        return () => observer.disconnect();
    }, []);

    return [ref, isInView];
}

// Componente animado
function AnimatedSection({ children, className = '', delay = 0 }) {
    const [ref, isInView] = useInView();

    return (
        <div
            ref={ref}
            className={`animate-on-scroll ${isInView ? 'is-visible' : ''} ${className}`}
            style={{ transitionDelay: `${delay}ms` }}
        >
            {children}
        </div>
    );
}

function Landing() {
    const [scrollY, setScrollY] = useState(0);

    useEffect(() => {
        const handleScroll = () => setScrollY(window.scrollY);
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="landing-page">
            {/* Navbar con efecto de scroll */}
            <nav className={`landing-nav ${scrollY > 50 ? 'scrolled' : ''}`}>
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

            {/* Hero Section con parallax */}
            <section className="hero-section">
                <div className="hero-content">
                    <AnimatedSection delay={0}>
                        <div className="hero-badge">🚀 La herramienta que necesitas</div>
                    </AnimatedSection>

                    <AnimatedSection delay={100}>
                        <h1 className="hero-title">
                            Automatiza tus <span className="gradient-text">Follow-Ups</span> y nunca pierdas un cliente
                        </h1>
                    </AnimatedSection>

                    <AnimatedSection delay={200}>
                        <p className="hero-subtitle">
                            El CRM diseñado para Project Managers que quieren mantener el control de sus contactos,
                            tareas y recordatorios. Gestiona desde la web o Telegram.
                        </p>
                    </AnimatedSection>

                    <AnimatedSection delay={300}>
                        <div className="hero-cta">
                            <Link to="/registro" className="btn btn-primary btn-lg pulse-animation">
                                Comenzar Gratis →
                            </Link>
                            <Link to="/precios" className="btn btn-secondary btn-lg">
                                Ver Planes
                            </Link>
                        </div>
                    </AnimatedSection>

                    <AnimatedSection delay={400}>
                        <div className="hero-trust">
                            <span>✓ Sin tarjeta de crédito</span>
                            <span>✓ Setup en 2 minutos</span>
                            <span>✓ Soporte por Telegram</span>
                        </div>
                    </AnimatedSection>
                </div>

                <div className="hero-image" style={{ transform: `translateY(${scrollY * 0.1}px)` }}>
                    <div className="hero-mockup floating-animation">
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
                    <AnimatedSection>
                        <div className="section-header">
                            <h2>Todo lo que necesitas para gestionar tus follow-ups</h2>
                            <p>Funcionalidades diseñadas para project managers que no quieren perder oportunidades</p>
                        </div>
                    </AnimatedSection>

                    <div className="features-grid">
                        {[
                            { icon: '📋', title: 'Vista Kanban', desc: 'Visualiza todas tus tareas en un tablero drag & drop. Mueve tareas entre estados con un click.' },
                            { icon: '📱', title: 'Bot de Telegram', desc: 'Gestiona todo desde Telegram. Crea tareas, contactos y recibe recordatorios sin abrir la web.' },
                            { icon: '📧', title: 'Emails Automáticos', desc: 'Envía recordatorios automáticos a tus contactos. Plantillas personalizables con variables.' },
                            { icon: '⏰', title: 'Recordatorios Múltiples', desc: 'Configura varios recordatorios por tarea: 3 días antes, 1 día antes, el mismo día.' },
                            { icon: '👥', title: 'Gestión de Contactos', desc: 'Centraliza toda la información de tus clientes con historial de interacciones.' },
                            { icon: '🗂', title: 'Proyectos', desc: 'Agrupa tareas por proyecto. Mantén organizados todos los seguimientos de cada cliente.' },
                        ].map((feature, i) => (
                            <AnimatedSection key={i} delay={i * 100}>
                                <div className="feature-card">
                                    <div className="feature-icon">{feature.icon}</div>
                                    <h3>{feature.title}</h3>
                                    <p>{feature.desc}</p>
                                </div>
                            </AnimatedSection>
                        ))}
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="how-section">
                <div className="section-container">
                    <AnimatedSection>
                        <div className="section-header">
                            <h2>¿Cómo funciona?</h2>
                            <p>Comienza en menos de 2 minutos</p>
                        </div>
                    </AnimatedSection>

                    <div className="steps-grid">
                        {[
                            { num: 1, title: 'Regístrate gratis', desc: 'Solo necesitas tu Telegram ID para comenzar' },
                            { num: 2, title: 'Conecta el Bot', desc: 'Inicia nuestro bot en Telegram con /start' },
                            { num: 3, title: 'Crea tu primer contacto', desc: 'Agrega contactos y tareas desde la web o el bot' },
                            { num: 4, title: 'Recibe recordatorios', desc: 'El sistema te avisa automáticamente por Telegram y email' },
                        ].map((step, i) => (
                            <>
                                {i > 0 && <div className="step-arrow" key={`arrow-${i}`}>→</div>}
                                <AnimatedSection key={i} delay={i * 150}>
                                    <div className="step-card">
                                        <div className="step-number">{step.num}</div>
                                        <h3>{step.title}</h3>
                                        <p>{step.desc}</p>
                                    </div>
                                </AnimatedSection>
                            </>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="stats-section">
                <div className="section-container">
                    <div className="stats-grid-landing">
                        <AnimatedSection delay={0}>
                            <div className="stat-item">
                                <span className="stat-number">500+</span>
                                <span className="stat-label">Usuarios activos</span>
                            </div>
                        </AnimatedSection>
                        <AnimatedSection delay={100}>
                            <div className="stat-item">
                                <span className="stat-number">10K+</span>
                                <span className="stat-label">Tareas gestionadas</span>
                            </div>
                        </AnimatedSection>
                        <AnimatedSection delay={200}>
                            <div className="stat-item">
                                <span className="stat-number">98%</span>
                                <span className="stat-label">Satisfacción</span>
                            </div>
                        </AnimatedSection>
                        <AnimatedSection delay={300}>
                            <div className="stat-item">
                                <span className="stat-number">24/7</span>
                                <span className="stat-label">Bot disponible</span>
                            </div>
                        </AnimatedSection>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="section-container">
                    <AnimatedSection>
                        <h2>¿Listo para no perder más clientes?</h2>
                        <p>Únete a cientos de project managers que ya automatizan sus follow-ups</p>
                        <Link to="/registro" className="btn btn-primary btn-lg">
                            Comenzar Gratis Ahora →
                        </Link>
                    </AnimatedSection>
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
