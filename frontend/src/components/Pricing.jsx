import { useState } from 'react';
import { Link } from 'react-router-dom';

function Pricing() {
    const [annual, setAnnual] = useState(false);

    const plans = [
        {
            name: 'Starter',
            description: 'Para freelancers y emprendedores',
            priceMonthly: 0,
            priceAnnual: 0,
            features: [
                '50 contactos',
                '100 tareas al mes',
                'Bot de Telegram',
                'Recordatorios por Telegram',
                'Vista Kanban',
                'Soporte por email'
            ],
            notIncluded: [
                'Emails automáticos',
                'Plantillas personalizadas',
                'Múltiples recordatorios',
                'Proyectos ilimitados'
            ],
            cta: 'Comenzar Gratis',
            highlighted: false
        },
        {
            name: 'Professional',
            description: 'Para project managers y equipos pequeños',
            priceMonthly: 9,
            priceAnnual: 7,
            features: [
                'Contactos ilimitados',
                'Tareas ilimitadas',
                'Bot de Telegram',
                'Recordatorios por Telegram',
                'Emails automáticos',
                'Plantillas personalizadas',
                'Múltiples recordatorios por tarea',
                '10 Proyectos',
                'Soporte prioritario'
            ],
            notIncluded: [
                'API Access',
                'Webhooks'
            ],
            cta: 'Elegir Professional',
            highlighted: true
        },
        {
            name: 'Business',
            description: 'Para empresas y agencias',
            priceMonthly: 29,
            priceAnnual: 24,
            features: [
                'Todo de Professional',
                'Proyectos ilimitados',
                'Múltiples usuarios',
                'API Access',
                'Webhooks',
                'Dominio email personalizado',
                'Soporte 24/7',
                'Onboarding personalizado'
            ],
            notIncluded: [],
            cta: 'Contactar Ventas',
            highlighted: false
        }
    ];

    return (
        <div className="landing-page">
            {/* Navbar */}
            <nav className="landing-nav">
                <div className="landing-nav-container">
                    <Link to="/" className="landing-logo">
                        📌 <span>CRM Follow-Up</span>
                    </Link>
                    <div className="landing-nav-links">
                        <Link to="/">Inicio</Link>
                        <Link to="/login" className="btn btn-secondary btn-sm">Iniciar Sesión</Link>
                        <Link to="/registro" className="btn btn-primary btn-sm">Comenzar Gratis</Link>
                    </div>
                </div>
            </nav>

            {/* Pricing Header */}
            <section className="pricing-header">
                <h1>Planes simples y transparentes</h1>
                <p>Elige el plan que mejor se adapte a tu negocio. Sin sorpresas.</p>

                {/* Toggle */}
                <div className="pricing-toggle">
                    <span className={!annual ? 'active' : ''}>Mensual</span>
                    <button
                        className={`toggle-switch ${annual ? 'active' : ''}`}
                        onClick={() => setAnnual(!annual)}
                    >
                        <span className="toggle-knob"></span>
                    </button>
                    <span className={annual ? 'active' : ''}>
                        Anual <span className="save-badge">Ahorra 20%</span>
                    </span>
                </div>
            </section>

            {/* Pricing Cards */}
            <section className="pricing-cards">
                <div className="pricing-grid">
                    {plans.map((plan) => (
                        <div
                            key={plan.name}
                            className={`pricing-card ${plan.highlighted ? 'highlighted' : ''}`}
                        >
                            {plan.highlighted && <div className="popular-badge">Más Popular</div>}

                            <div className="pricing-card-header">
                                <h3>{plan.name}</h3>
                                <p>{plan.description}</p>
                            </div>

                            <div className="pricing-price">
                                <span className="currency">$</span>
                                <span className="amount">{annual ? plan.priceAnnual : plan.priceMonthly}</span>
                                <span className="period">/mes</span>
                            </div>

                            {annual && plan.priceMonthly > 0 && (
                                <div className="pricing-billed">
                                    Facturado anualmente (${(annual ? plan.priceAnnual : plan.priceMonthly) * 12}/año)
                                </div>
                            )}

                            <Link
                                to={plan.priceMonthly === 0 ? '/registro' : '/registro?plan=' + plan.name.toLowerCase()}
                                className={`btn ${plan.highlighted ? 'btn-primary' : 'btn-secondary'} btn-block`}
                            >
                                {plan.cta}
                            </Link>

                            <ul className="pricing-features">
                                {plan.features.map((feature, i) => (
                                    <li key={i} className="included">
                                        <span className="check">✓</span> {feature}
                                    </li>
                                ))}
                                {plan.notIncluded.map((feature, i) => (
                                    <li key={i} className="not-included">
                                        <span className="x">✕</span> {feature}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </section>

            {/* FAQ */}
            <section className="faq-section">
                <div className="section-container">
                    <h2>Preguntas Frecuentes</h2>
                    <div className="faq-grid">
                        <div className="faq-item">
                            <h4>¿Puedo cambiar de plan después?</h4>
                            <p>Sí, puedes actualizar o bajar tu plan en cualquier momento. Los cambios se reflejan en tu próximo ciclo de facturación.</p>
                        </div>
                        <div className="faq-item">
                            <h4>¿Cómo funciona el bot de Telegram?</h4>
                            <p>Una vez registrado, solo necesitas iniciar nuestro bot con /start usando tu Telegram. Podrás gestionar todo desde el chat.</p>
                        </div>
                        <div className="faq-item">
                            <h4>¿Necesito tarjeta de crédito para el plan gratuito?</h4>
                            <p>No, el plan Starter es 100% gratis y no requiere ningún método de pago.</p>
                        </div>
                        <div className="faq-item">
                            <h4>¿Los emails salen de mi dominio?</h4>
                            <p>Los emails salen de nuestro dominio, pero tu contacto puede responder directamente a tu email personal.</p>
                        </div>
                    </div>
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
                            <Link to="/#features">Funcionalidades</Link>
                        </div>
                        <div className="footer-col">
                            <h4>Cuenta</h4>
                            <Link to="/login">Iniciar Sesión</Link>
                            <Link to="/registro">Registrarse</Link>
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

export default Pricing;
