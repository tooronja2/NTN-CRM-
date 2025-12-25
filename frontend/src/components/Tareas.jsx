import { useState, useEffect } from 'react';
import { getTareas, getTareasKanban, createTarea, updateTarea, deleteTarea, cambiarEstadoTarea, getContactos } from '../api/client';

function Tareas() {
    const [tareas, setTareas] = useState([]);
    const [kanban, setKanban] = useState(null);
    const [contactos, setContactos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState('kanban'); // 'kanban' o 'list'
    const [showModal, setShowModal] = useState(false);
    const [editingTarea, setEditingTarea] = useState(null);
    const [formData, setFormData] = useState({
        titulo: '',
        descripcion: '',
        contacto_id: '',
        fecha_vencimiento: '',
        prioridad: 'media',
        estado: 'pendiente',
        canal_notificacion: 'telegram'
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [tareasData, kanbanData, contactosData] = await Promise.all([
                getTareas(),
                getTareasKanban(),
                getContactos()
            ]);
            setTareas(tareasData);
            setKanban(kanbanData);
            setContactos(contactosData);
        } catch (err) {
            console.error('Error cargando datos:', err);
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

    const handleDragOver = (e) => e.preventDefault();

    const openModal = (tarea = null) => {
        if (tarea) {
            setEditingTarea(tarea);
            setFormData({
                titulo: tarea.titulo || '',
                descripcion: tarea.descripcion || '',
                contacto_id: tarea.contacto_id || '',
                fecha_vencimiento: tarea.fecha_vencimiento?.slice(0, 16) || '',
                prioridad: tarea.prioridad || 'media',
                estado: tarea.estado || 'pendiente',
                canal_notificacion: tarea.canal_notificacion || 'telegram'
            });
        } else {
            setEditingTarea(null);
            setFormData({
                titulo: '',
                descripcion: '',
                contacto_id: '',
                fecha_vencimiento: '',
                prioridad: 'media',
                estado: 'pendiente',
                canal_notificacion: 'telegram'
            });
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditingTarea(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = {
                ...formData,
                contacto_id: formData.contacto_id ? parseInt(formData.contacto_id) : null,
                fecha_vencimiento: formData.fecha_vencimiento || null
            };

            if (editingTarea) {
                await updateTarea(editingTarea.id, data);
            } else {
                await createTarea(data);
            }
            closeModal();
            loadData();
        } catch (err) {
            alert('Error guardando tarea: ' + err.message);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('¿Eliminar esta tarea?')) return;
        try {
            await deleteTarea(id);
            loadData();
        } catch (err) {
            alert('Error eliminando tarea');
        }
    };

    const columnas = [
        { key: 'pendiente', label: 'Pendiente', emoji: '🔴' },
        { key: 'en_seguimiento', label: 'En Seguimiento', emoji: '🟡' },
        { key: 'esperando_respuesta', label: 'Esperando', emoji: '🟠' },
        { key: 'completado', label: 'Completado', emoji: '🟢' }
    ];

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="main-header">
                <h1 className="main-title">📋 Tareas</h1>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{ display: 'flex', background: 'var(--gray-100)', borderRadius: '8px', padding: '4px' }}>
                        <button
                            className={`btn btn-sm ${viewMode === 'kanban' ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setViewMode('kanban')}
                            style={{ borderRadius: '6px' }}
                        >
                            📊 Kanban
                        </button>
                        <button
                            className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setViewMode('list')}
                            style={{ borderRadius: '6px' }}
                        >
                            📝 Lista
                        </button>
                    </div>
                    <button className="btn btn-primary" onClick={() => openModal()}>
                        + Nueva Tarea
                    </button>
                </div>
            </div>

            {/* Kanban View */}
            {viewMode === 'kanban' && kanban && (
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
                                        onClick={() => openModal(tarea)}
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
                                    <div style={{ padding: '24px', textAlign: 'center', color: 'var(--gray-400)', fontSize: '0.875rem' }}>
                                        Arrastra tareas aquí
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* List View */}
            {viewMode === 'list' && (
                <div className="list-container">
                    {tareas.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📋</div>
                            <div className="empty-state-title">Sin tareas</div>
                            <button className="btn btn-primary" onClick={() => openModal()}>
                                + Nueva Tarea
                            </button>
                        </div>
                    ) : (
                        tareas.map((tarea) => (
                            <div key={tarea.id} className="list-item">
                                <div className={`badge badge-${tarea.prioridad === 'urgente' ? 'danger' : tarea.prioridad === 'alta' ? 'warning' : 'gray'}`}>
                                    {tarea.prioridad}
                                </div>
                                <div className="list-item-content">
                                    <div className="list-item-title">{tarea.titulo}</div>
                                    <div className="list-item-subtitle">
                                        {tarea.fecha_vencimiento?.slice(0, 10)}
                                        {tarea.contactos && ` • ${tarea.contactos.nombre}`}
                                        <span className={`badge badge-${tarea.estado === 'completado' ? 'success' : 'gray'}`} style={{ marginLeft: '8px' }}>
                                            {tarea.estado.replace('_', ' ')}
                                        </span>
                                    </div>
                                </div>
                                <div className="list-item-actions">
                                    <button className="btn btn-sm btn-secondary" onClick={() => openModal(tarea)}>
                                        ✏️
                                    </button>
                                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(tarea.id)}>
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">
                                {editingTarea ? 'Editar Tarea' : 'Nueva Tarea'}
                            </h2>
                            <button className="modal-close" onClick={closeModal}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label className="form-label">Título *</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.titulo}
                                        onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Descripción</label>
                                    <textarea
                                        className="form-textarea"
                                        value={formData.descripcion}
                                        onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                                        rows="2"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Contacto</label>
                                    <select
                                        className="form-select"
                                        value={formData.contacto_id}
                                        onChange={(e) => setFormData({ ...formData, contacto_id: e.target.value })}
                                    >
                                        <option value="">Sin contacto</option>
                                        {contactos.map((c) => (
                                            <option key={c.id} value={c.id}>{c.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                    <div className="form-group">
                                        <label className="form-label">Fecha y Hora</label>
                                        <input
                                            type="datetime-local"
                                            className="form-input"
                                            value={formData.fecha_vencimiento}
                                            onChange={(e) => setFormData({ ...formData, fecha_vencimiento: e.target.value })}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Prioridad</label>
                                        <select
                                            className="form-select"
                                            value={formData.prioridad}
                                            onChange={(e) => setFormData({ ...formData, prioridad: e.target.value })}
                                        >
                                            <option value="baja">Baja</option>
                                            <option value="media">Media</option>
                                            <option value="alta">Alta</option>
                                            <option value="urgente">Urgente</option>
                                        </select>
                                    </div>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                    <div className="form-group">
                                        <label className="form-label">Estado</label>
                                        <select
                                            className="form-select"
                                            value={formData.estado}
                                            onChange={(e) => setFormData({ ...formData, estado: e.target.value })}
                                        >
                                            <option value="pendiente">Pendiente</option>
                                            <option value="en_seguimiento">En Seguimiento</option>
                                            <option value="esperando_respuesta">Esperando Respuesta</option>
                                            <option value="completado">Completado</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Notificar por</label>
                                        <select
                                            className="form-select"
                                            value={formData.canal_notificacion}
                                            onChange={(e) => setFormData({ ...formData, canal_notificacion: e.target.value })}
                                        >
                                            <option value="telegram">Telegram</option>
                                            <option value="email">Email</option>
                                            <option value="ambos">Ambos</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingTarea ? 'Guardar' : 'Crear Tarea'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Tareas;
