import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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
        // Check login status on mount
        setLoggedIn(isLoggedIn());
    }, []);

    const handleLogin = () => {
        setLoggedIn(true);
    };

    const handleLogout = () => {
        setLoggedIn(false);
    };

    if (!loggedIn) {
        return <Login onLogin={handleLogin} />;
    }

    return (
        <BrowserRouter>
            <div className="app-container">
                {/* Mobile menu toggle */}
                <button
                    className="menu-toggle"
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                >
                    ☰
                </button>

                {/* Sidebar overlay for mobile */}
                <div
                    className={`sidebar-overlay ${sidebarOpen ? 'show' : ''}`}
                    onClick={() => setSidebarOpen(false)}
                />

                {/* Sidebar */}
                <Sidebar
                    isOpen={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                    onLogout={handleLogout}
                />

                {/* Main content */}
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/contactos" element={<Contactos />} />
                        <Route path="/tareas" element={<Tareas />} />
                        <Route path="/proyectos" element={<Proyectos />} />
                        <Route path="/plantillas" element={<Plantillas />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}

export default App;
