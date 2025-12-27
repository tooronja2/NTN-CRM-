import { NavLink, useLocation } from 'react-router-dom';
import { logout } from '../api/client';

function Sidebar({ isOpen, onClose, onLogout }) {
    const location = useLocation();

    const handleLogout = () => {
        logout();
        onLogout();
    };

    const navItems = [
        { path: '/dashboard', icon: '📊', label: 'Dashboard' },
        { path: '/contactos', icon: '👥', label: 'Contactos' },
        { path: '/tareas', icon: '📋', label: 'Tareas' },
        { path: '/proyectos', icon: '🗂', label: 'Proyectos' },
        { path: '/plantillas', icon: '📝', label: 'Plantillas' },
    ];

    return (
        <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <span>⚡ Syncra</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    <div className="nav-section-title">Menú Principal</div>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            onClick={onClose}
                        >
                            <span>{item.icon}</span>
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </div>

                <div className="nav-section">
                    <div className="nav-section-title">Configuración</div>
                    <div className="nav-link" onClick={handleLogout} style={{ cursor: 'pointer' }}>
                        <span>🚪</span>
                        <span>Cerrar Sesión</span>
                    </div>
                </div>
            </nav>

            <div style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', textAlign: 'center' }}>
                    También disponible en<br />
                    <strong>Telegram</strong> 📱
                </div>
            </div>
        </aside>
    );
}

export default Sidebar;
