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

// Iconos SVG profesionales
const Icons = {
    kanban: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="5" height="18" rx="1" />
            <rect x="10" y="3" width="5" height="12" rx="1" />
            <rect x="17" y="3" width="5" height="8" rx="1" />
        </svg>
    ),
    telegram: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 5L2 12.5l7 1M21 5l-11 14.5v-6L21 5z" />
        </svg>
    ),
    email: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2" />
            <path d="M22 6l-10 7L2 6" />
        </svg>
    ),
    clock: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
        </svg>
    ),
    users: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="9" cy="7" r="4" />
            <path d="M3 21v-2a4 4 0 014-4h4a4 4 0 014 4v2" />
            <circle cx="17" cy="7" r="3" />
            <path d="M21 21v-2a3 3 0 00-2-2.83" />
        </svg>
    ),
    folder: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
        </svg>
    ),
    check: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
        </svg>
    ),
    arrow: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
    )
};

function Landing() {
    const [scrollY, setScrollY] = useState(0);
    const [isNavSolid, setIsNavSolid] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrollY(window.scrollY);
            setIsNavSolid(window.scrollY > 100);
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const features = [
        { icon: Icons.kanban, title: 'Vista Kanban', desc: 'Visualiza todas tus tareas en un tablero drag & drop. Organiza el flujo de trabajo con estados personalizables.' },
        { icon: Icons.telegram, title: 'Bot de Telegram', desc: 'Gestiona todo desde Telegram. Crea tareas, contactos y recibe recordatorios sin abrir la web.' },
        { icon: Icons.email, title: 'Emails Automáticos', desc: 'Envía recordatorios automáticos a tus contactos. Plantillas personalizables con variables dinámicas.' },
        { icon: Icons.clock, title: 'Recordatorios Múltiples', desc: 'Configura varios recordatorios por tarea: 3 días antes, 1 día antes, el mismo día.' },
        { icon: Icons.users, title: 'Gestión de Contactos', desc: 'Centraliza toda la información de tus clientes con historial completo de interacciones.' },
        { icon: Icons.folder, title: 'Proyectos', desc: 'Agrupa tareas por proyecto. Mantén organizados todos los seguimientos de cada cliente.' },
    ];

    const steps = [
        { num: 1, title: 'Regístrate gratis', desc: 'Solo necesitas tu Telegram ID para comenzar' },
        { num: 2, title: 'Conecta el Bot', desc: 'Inicia nuestro bot en Telegram con /start' },
        { num: 3, title: 'Crea tu primer contacto', desc: 'Agrega contactos y tareas desde la web o el bot' },
        { num: 4, title: 'Recibe recordatorios', desc: 'El sistema te avisa automáticamente por Telegram y email' },
    ];

    return (
        <div className="landing-page">
            {/* Navbar - Transparente al inicio, sólido al scrollear */}
            <nav className={`landing-nav ${isNavSolid ? 'nav-solid' : 'nav-transparent'}`}>
                <div className="landing-nav-container">
                    <Link to="/" className="landing-logo">
                        <img src="/Evolthix.png" alt="Evolthix" className="nav-logo-img" />
                    </Link>
                    <div className="landing-nav-links">
                        <Link to="/precios">Precios</Link>
                        <Link to="/login" className="btn btn-ghost btn-sm">Iniciar Sesión</Link>
                        <Link to="/registro" className="btn btn-primary btn-sm">Comenzar Gratis</Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section con Video de Fondo */}
            <section className="hero-video-section">
                {/* Video/Imagen de fondo */}
                <div className="hero-video-bg">
                    {/* TODO: Reemplazar con video cuando esté disponible */}
                    {/* <video autoPlay muted loop playsInline>
                        <source src="/videos/hero-video.mp4" type="video/mp4" />
                    </video> */}
                    <div className="hero-placeholder-bg"></div>
                    <div className="hero-overlay"></div>
                </div>

                <div className="hero-video-content">
                    <AnimatedSection delay={0}>
                        <img src="/Evolthix.png" alt="Evolthix" className="hero-brand-logo" />
                    </AnimatedSection>

                    <AnimatedSection delay={200}>
                        <h1 className="hero-video-title">
                            Automatización Inteligente<br />
                            <span>de Seguimientos</span>
                        </h1>
                    </AnimatedSection>

                    <AnimatedSection delay={300}>
                        <p className="hero-video-subtitle">
                            El CRM diseñado para Project Managers que quieren mantener el control
                            de sus contactos, tareas y recordatorios.
                        </p>
                    </AnimatedSection>

                    <AnimatedSection delay={400}>
                        <div className="hero-video-cta">
                            <Link to="/registro" className="btn btn-light btn-lg">
                                Comenzar Ahora
                                <span className="btn-icon">{Icons.arrow}</span>
                            </Link>
                        </div>
                    </AnimatedSection>

                    <AnimatedSection delay={500}>
                        <div className="hero-trust-badges">
                            <span><span className="trust-icon">{Icons.check}</span> Sin tarjeta de crédito</span>
                            <span><span className="trust-icon">{Icons.check}</span> Setup en 2 minutos</span>
                            <span><span className="trust-icon">{Icons.check}</span> Soporte dedicado</span>
                        </div>
                    </AnimatedSection>
                </div>

                {/* Scroll indicator */}
                <div className="scroll-indicator">
                    <div className="scroll-mouse">
                        <div className="scroll-wheel"></div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section" id="features">
                <div className="section-container">
                    <AnimatedSection>
                        <div className="section-header">
                            <h2>Todo lo que necesitas para gestionar tus follow-ups</h2>
                            <p>Funcionalidades diseñadas para profesionales que no quieren perder oportunidades</p>
                        </div>
                    </AnimatedSection>

                    <div className="features-grid">
                        {features.map((feature, i) => (
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
                        {steps.map((step, i) => (
                            <AnimatedSection key={i} delay={i * 150}>
                                <div className="step-card">
                                    <div className="step-number">{step.num}</div>
                                    <h3>{step.title}</h3>
                                    <p>{step.desc}</p>
                                </div>
                            </AnimatedSection>
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
                        <h2>¿Listo para optimizar tu gestión?</h2>
                        <p>Únete a cientos de profesionales que ya automatizan sus follow-ups</p>
                        <Link to="/registro" className="btn btn-primary btn-lg">
                            Comenzar Gratis Ahora
                            <span className="btn-icon">{Icons.arrow}</span>
                        </Link>
                    </AnimatedSection>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="footer-container">
                    <div className="footer-brand">
                        <img src="/Evolthix.png" alt="Evolthix" className="footer-brand-logo" />
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
                    <p>© 2024 Evolthix. Todos los derechos reservados.</p>
                </div>
            </footer>
        </div>
    );
}

export default Landing;
