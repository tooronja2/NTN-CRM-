import { useState, useEffect } from 'react';
import { getDashboard, getTareasKanban, cambiarEstadoTarea } from '../api/client';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [kanban, setKanban] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [dashboardData, kanbanData] = await Promise.all([
                getDashboard(),
                getTareasKanban()
            ]);
            setStats(dashboardData);
            setKanban(kanbanData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDragStart = (e, tareaId, estadoActual) => {
        e.dataTransfer.setData('tareaId', tareaId);
        e.dataTransfer.setData('estadoActual', estadoActual);
    };

    const handleDrop = async (e, nuevoEstado) => {
        e.preventDefault();
        const tareaId = e.dataTransfer.getData('tareaId');
        const estadoActual = e.dataTransfer.getData('estadoActual');

        if (estadoActual === nuevoEstado) return;

        try {
            await cambiarEstadoTarea(tareaId, nuevoEstado);
            loadData();
        } catch (err) {
            console.error('Error cambiando estado:', err);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">⚠️</div>
                <div className="empty-state-title">Error cargando datos</div>
                <p className="empty-state-text">{error}</p>
                <button className="btn btn-primary" onClick={loadData}>Reintentar</button>
            </div>
        );
    }

    const columnas = [
        { key: 'pendiente', label: 'Pendiente', emoji: '🔴' },
        { key: 'en_seguimiento', label: 'En Seguimiento', emoji: '🟡' },
        { key: 'esperando_respuesta', label: 'Esperando Respuesta', emoji: '🟠' },
        { key: 'completado', label: 'Completado', emoji: '🟢' }
    ];

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="main-header">
                <h1 className="main-title">Dashboard</h1>
                <button className="btn btn-secondary" onClick={loadData}>🔄 Actualizar</button>
            </div>

            {/* Stats */}
            {stats && (
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon contacts">👥</div>
                        <div className="stat-content">
                            <h3>{stats.total_contactos}</h3>
                            <p>Contactos</p>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon tasks">📋</div>
                        <div className="stat-content">
                            <h3>{stats.total_tareas_pendientes}</h3>
                            <p>Tareas Pendientes</p>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon today">📅</div>
                        <div className="stat-content">
                            <h3>{stats.total_tareas_hoy}</h3>
                            <p>Tareas Hoy</p>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon projects">🗂</div>
                        <div className="stat-content">
                            <h3>{stats.total_proyectos_activos}</h3>
                            <p>Proyectos Activos</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Próximos vencimientos */}
            {stats?.proximos_vencimientos?.length > 0 && (
                <div className="card" style={{ marginBottom: '24px' }}>
                    <div className="card-header">
                        <h2 className="card-title">📅 Próximos Vencimientos (7 días)</h2>
                    </div>
                    <div className="card-body" style={{ padding: 0 }}>
                        {stats.proximos_vencimientos.map((tarea) => (
                            <div key={tarea.id} className="list-item">
                                <div className={`badge badge-${tarea.prioridad === 'urgente' ? 'danger' : tarea.prioridad === 'alta' ? 'warning' : 'gray'}`}>
                                    {tarea.prioridad}
                                </div>
                                <div className="list-item-content">
                                    <div className="list-item-title">{tarea.titulo}</div>
                                    <div className="list-item-subtitle">
                                        {tarea.fecha_vencimiento?.slice(0, 10)}
                                        {tarea.contactos && ` • ${tarea.contactos.nombre}`}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Kanban Board */}
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">📋 Pipeline de Tareas</h2>
                </div>
                <div className="card-body">
                    {kanban && (
                        <div className="kanban-board">
                            {columnas.map((col) => (
                                <div
                                    key={col.key}
                                    className="kanban-column"
                                    onDrop={(e) => handleDrop(e, col.key)}
                                    onDragOver={handleDragOver}
                                >
                                    <div className={`kanban-column-header ${col.key}`}>
                                        <span>{col.emoji} {col.label}</span>
                                        <span className="kanban-count">{kanban[col.key]?.length || 0}</span>
                                    </div>
                                    <div className="kanban-cards">
                                        {kanban[col.key]?.map((tarea) => (
                                            <div
                                                key={tarea.id}
                                                className={`kanban-card prioridad-${tarea.prioridad}`}
                                                draggable
                                                onDragStart={(e) => handleDragStart(e, tarea.id, col.key)}
                                            >
                                                <div className="kanban-card-title">{tarea.titulo}</div>
                                                <div className="kanban-card-meta">
                                                    {tarea.fecha_vencimiento && (
                                                        <span>📅 {tarea.fecha_vencimiento.slice(0, 10)}</span>
                                                    )}
                                                    {tarea.contactos && (
                                                        <span>👤 {tarea.contactos.nombre}</span>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                        {(!kanban[col.key] || kanban[col.key].length === 0) && (
                                            <div className="empty-state" style={{ padding: '24px', background: 'transparent' }}>
                                                <p style={{ fontSize: '0.8rem' }}>Sin tareas</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
