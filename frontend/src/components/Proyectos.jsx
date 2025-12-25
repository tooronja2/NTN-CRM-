import { useState, useEffect } from 'react';
import { getProyectos, createProyecto, updateProyecto, deleteProyecto, getContactos } from '../api/client';

function Proyectos() {
    const [proyectos, setProyectos] = useState([]);
    const [contactos, setContactos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingProyecto, setEditingProyecto] = useState(null);
    const [formData, setFormData] = useState({
        nombre: '',
        descripcion: '',
        contacto_id: '',
        estado: 'activo'
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [proyectosData, contactosData] = await Promise.all([
                getProyectos(),
                getContactos()
            ]);
            setProyectos(proyectosData);
            setContactos(contactosData);
        } catch (err) {
            console.error('Error cargando datos:', err);
        } finally {
            setLoading(false);
        }
    };

    const openModal = (proyecto = null) => {
        if (proyecto) {
            setEditingProyecto(proyecto);
            setFormData({
                nombre: proyecto.nombre || '',
                descripcion: proyecto.descripcion || '',
                contacto_id: proyecto.contacto_id || '',
                estado: proyecto.estado || 'activo'
            });
        } else {
            setEditingProyecto(null);
            setFormData({ nombre: '', descripcion: '', contacto_id: '', estado: 'activo' });
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditingProyecto(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = {
                ...formData,
                contacto_id: formData.contacto_id ? parseInt(formData.contacto_id) : null
            };

            if (editingProyecto) {
                await updateProyecto(editingProyecto.id, data);
            } else {
                await createProyecto(data);
            }
            closeModal();
            loadData();
        } catch (err) {
            alert('Error guardando proyecto: ' + err.message);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('¿Eliminar este proyecto?')) return;
        try {
            await deleteProyecto(id);
            loadData();
        } catch (err) {
            alert('Error eliminando proyecto');
        }
    };

    const estadoColors = {
        activo: 'success',
        pausado: 'warning',
        completado: 'primary',
        cancelado: 'danger'
    };

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
                <h1 className="main-title">🗂 Proyectos</h1>
                <button className="btn btn-primary" onClick={() => openModal()}>
                    + Nuevo Proyecto
                </button>
            </div>

            {/* Grid de proyectos */}
            {proyectos.length === 0 ? (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-state-icon">🗂</div>
                        <div className="empty-state-title">Sin proyectos</div>
                        <p className="empty-state-text">Crea tu primer proyecto para organizar tus tareas</p>
                        <button className="btn btn-primary" onClick={() => openModal()}>
                            + Nuevo Proyecto
                        </button>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
                    {proyectos.map((proyecto) => (
                        <div key={proyecto.id} className="card" style={{ cursor: 'pointer' }} onClick={() => openModal(proyecto)}>
                            <div className="card-body">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--gray-900)' }}>
                                        {proyecto.nombre}
                                    </h3>
                                    <span className={`badge badge-${estadoColors[proyecto.estado] || 'gray'}`}>
                                        {proyecto.estado}
                                    </span>
                                </div>
                                {proyecto.descripcion && (
                                    <p style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '12px' }}>
                                        {proyecto.descripcion.length > 100
                                            ? proyecto.descripcion.slice(0, 100) + '...'
                                            : proyecto.descripcion}
                                    </p>
                                )}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    {proyecto.contactos && (
                                        <span style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
                                            👤 {proyecto.contactos.nombre}
                                        </span>
                                    )}
                                    <button
                                        className="btn btn-sm btn-danger"
                                        onClick={(e) => { e.stopPropagation(); handleDelete(proyecto.id); }}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">
                                {editingProyecto ? 'Editar Proyecto' : 'Nuevo Proyecto'}
                            </h2>
                            <button className="modal-close" onClick={closeModal}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label className="form-label">Nombre *</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.nombre}
                                        onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Descripción</label>
                                    <textarea
                                        className="form-textarea"
                                        value={formData.descripcion}
                                        onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                                        rows="3"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Contacto Principal</label>
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
                                <div className="form-group">
                                    <label className="form-label">Estado</label>
                                    <select
                                        className="form-select"
                                        value={formData.estado}
                                        onChange={(e) => setFormData({ ...formData, estado: e.target.value })}
                                    >
                                        <option value="activo">Activo</option>
                                        <option value="pausado">Pausado</option>
                                        <option value="completado">Completado</option>
                                        <option value="cancelado">Cancelado</option>
                                    </select>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingProyecto ? 'Guardar' : 'Crear Proyecto'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Proyectos;
