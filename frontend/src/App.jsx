import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Componentes públicos (Landing)
import Landing from './components/Landing';
import Pricing from './components/Pricing';
import Register from './components/Register';

// Componentes privados (Dashboard)
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Contactos from './components/Contactos';
import Tareas from './components/Tareas';
import Proyectos from './components/Proyectos';
import Plantillas from './components/Plantillas';
import Login from './components/Login';

import { isLoggedIn } from './api/client';

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [loggedIn, setLoggedIn] = useState(isLoggedIn());

    useEffect(() => {
        setLoggedIn(isLoggedIn());
    }, []);

    const handleLogin = () => {
        setLoggedIn(true);
    };

    const handleLogout = () => {
        setLoggedIn(false);
    };

    // Layout para el dashboard (privado)
    const DashboardLayout = ({ children }) => (
        <div className="app-container">
            <button
                className="menu-toggle"
                onClick={() => setSidebarOpen(!sidebarOpen)}
            >
                ☰
            </button>
            <div
                className={`sidebar-overlay ${sidebarOpen ? 'show' : ''}`}
                onClick={() => setSidebarOpen(false)}
            />
            <Sidebar
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
                onLogout={handleLogout}
            />
            <main className="main-content">
                {children}
            </main>
        </div>
    );

    // Rutas protegidas
    const PrivateRoute = ({ children }) => {
        if (!loggedIn) {
            return <Navigate to="/login" replace />;
        }
        return <DashboardLayout>{children}</DashboardLayout>;
    };

    return (
        <BrowserRouter>
            <Routes>
                {/* Rutas públicas */}
                <Route path="/" element={<Landing />} />
                <Route path="/precios" element={<Pricing />} />
                <Route path="/registro" element={<Register onSuccess={() => window.location.href = '/login'} />} />
                <Route path="/login" element={
                    loggedIn ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />
                } />

                {/* Rutas privadas (Dashboard) */}
                <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                <Route path="/contactos" element={<PrivateRoute><Contactos /></PrivateRoute>} />
                <Route path="/tareas" element={<PrivateRoute><Tareas /></PrivateRoute>} />
                <Route path="/proyectos" element={<PrivateRoute><Proyectos /></PrivateRoute>} />
                <Route path="/plantillas" element={<PrivateRoute><Plantillas /></PrivateRoute>} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
