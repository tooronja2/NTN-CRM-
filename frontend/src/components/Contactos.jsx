import { useState, useEffect } from 'react';
import { getContactos, createContacto, updateContacto, deleteContacto } from '../api/client';

function Contactos() {
    const [contactos, setContactos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingContacto, setEditingContacto] = useState(null);
    const [formData, setFormData] = useState({
        nombre: '',
        email: '',
        telefono: '',
        empresa: '',
        notas: ''
    });

    useEffect(() => {
        loadContactos();
    }, []);

    const loadContactos = async () => {
        try {
            setLoading(true);
            const data = await getContactos(search);
            setContactos(data);
        } catch (err) {
            console.error('Error cargando contactos:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        loadContactos();
    };

    const openModal = (contacto = null) => {
        if (contacto) {
            setEditingContacto(contacto);
            setFormData({
                nombre: contacto.nombre || '',
                email: contacto.email || '',
                telefono: contacto.telefono || '',
                empresa: contacto.empresa || '',
                notas: contacto.notas || ''
            });
        } else {
            setEditingContacto(null);
            setFormData({ nombre: '', email: '', telefono: '', empresa: '', notas: '' });
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditingContacto(null);
        setFormData({ nombre: '', email: '', telefono: '', empresa: '', notas: '' });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingContacto) {
                await updateContacto(editingContacto.id, formData);
            } else {
                await createContacto(formData);
            }
            closeModal();
            loadContactos();
        } catch (err) {
            alert('Error guardando contacto: ' + err.message);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('¿Eliminar este contacto?')) return;
        try {
            await deleteContacto(id);
            loadContactos();
        } catch (err) {
            alert('Error eliminando contacto');
        }
    };

    const getInitials = (nombre) => {
        return nombre.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    };

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="main-header">
                <h1 className="main-title">👥 Contactos</h1>
                <button className="btn btn-primary" onClick={() => openModal()}>
                    + Nuevo Contacto
                </button>
            </div>

            {/* Search */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div className="card-body">
                    <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px' }}>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="Buscar contacto..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            style={{ flex: 1 }}
                        />
                        <button type="submit" className="btn btn-secondary">🔍 Buscar</button>
                    </form>
                </div>
            </div>

            {/* Lista */}
            <div className="list-container">
                {loading ? (
                    <div className="loading-container">
                        <div className="spinner"></div>
                    </div>
                ) : contactos.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">👥</div>
                        <div className="empty-state-title">Sin contactos</div>
                        <p className="empty-state-text">Crea tu primer contacto para empezar</p>
                        <button className="btn btn-primary" onClick={() => openModal()}>
                            + Nuevo Contacto
                        </button>
                    </div>
                ) : (
                    contactos.map((contacto) => (
                        <div key={contacto.id} className="list-item">
                            <div className="list-item-avatar">
                                {getInitials(contacto.nombre)}
                            </div>
                            <div className="list-item-content">
                                <div className="list-item-title">{contacto.nombre}</div>
                                <div className="list-item-subtitle">
                                    {contacto.email && <span>📧 {contacto.email}</span>}
                                    {contacto.empresa && <span style={{ marginLeft: '12px' }}>🏢 {contacto.empresa}</span>}
                                </div>
                            </div>
                            <div className="list-item-actions">
                                <button className="btn btn-sm btn-secondary" onClick={() => openModal(contacto)}>
                                    ✏️ Editar
                                </button>
                                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(contacto.id)}>
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">
                                {editingContacto ? 'Editar Contacto' : 'Nuevo Contacto'}
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
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        className="form-input"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        placeholder="cliente@ejemplo.com"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Teléfono</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.telefono}
                                        onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Empresa</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.empresa}
                                        onChange={(e) => setFormData({ ...formData, empresa: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Notas</label>
                                    <textarea
                                        className="form-textarea"
                                        value={formData.notas}
                                        onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                                        rows="3"
                                    />
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingContacto ? 'Guardar Cambios' : 'Crear Contacto'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Contactos;
