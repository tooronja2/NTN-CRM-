import { useState, useEffect } from 'react';
import { getPlantillas, createPlantilla, updatePlantilla, deletePlantilla, previewPlantilla } from '../api/client';

function Plantillas() {
    const [plantillas, setPlantillas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [showPreview, setShowPreview] = useState(false);
    const [previewContent, setPreviewContent] = useState(null);
    const [editingPlantilla, setEditingPlantilla] = useState(null);
    const [formData, setFormData] = useState({
        nombre: '',
        tipo: 'telegram',
        asunto: '',
        mensaje: '',
        es_default: false
    });

    const variablesDisponibles = [
        { nombre: 'titulo', desc: 'Título de la tarea' },
        { nombre: 'descripcion', desc: 'Descripción' },
        { nombre: 'fecha_vencimiento', desc: 'Fecha vencimiento' },
        { nombre: 'contacto_nombre', desc: 'Nombre del contacto' },
        { nombre: 'contacto_email', desc: 'Email del contacto' },
        { nombre: 'contacto_empresa', desc: 'Empresa' },
        { nombre: 'prioridad', desc: 'Prioridad' }
    ];

    useEffect(() => {
        loadPlantillas();
    }, []);

    const loadPlantillas = async () => {
        try {
            setLoading(true);
            const data = await getPlantillas();
            setPlantillas(data);
        } catch (err) {
            console.error('Error cargando plantillas:', err);
        } finally {
            setLoading(false);
        }
    };

    const openModal = (plantilla = null) => {
        if (plantilla) {
            setEditingPlantilla(plantilla);
            setFormData({
                nombre: plantilla.nombre || '',
                tipo: plantilla.tipo || 'telegram',
                asunto: plantilla.asunto || '',
                mensaje: plantilla.mensaje || '',
                es_default: plantilla.es_default || false
            });
        } else {
            setEditingPlantilla(null);
            setFormData({ nombre: '', tipo: 'telegram', asunto: '', mensaje: '', es_default: false });
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditingPlantilla(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingPlantilla) {
                await updatePlantilla(editingPlantilla.id, formData);
            } else {
                await createPlantilla(formData);
            }
            closeModal();
            loadPlantillas();
        } catch (err) {
            alert('Error guardando plantilla: ' + err.message);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('¿Eliminar esta plantilla?')) return;
        try {
            await deletePlantilla(id);
            loadPlantillas();
        } catch (err) {
            alert('Error eliminando plantilla');
        }
    };

    const handlePreview = async (plantilla) => {
        try {
            const preview = await previewPlantilla(plantilla.id);
            setPreviewContent({ ...preview, plantilla });
            setShowPreview(true);
        } catch (err) {
            alert('Error generando preview');
        }
    };

    const insertVariable = (variable) => {
        const insertText = `{{${variable}}}`;
        setFormData({ ...formData, mensaje: formData.mensaje + insertText });
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
                <h1 className="main-title">📝 Plantillas</h1>
                <button className="btn btn-primary" onClick={() => openModal()}>
                    + Nueva Plantilla
                </button>
            </div>

            {/* Info */}
            <div className="card" style={{ marginBottom: '24px', background: 'var(--primary-50)' }}>
                <div className="card-body">
                    <p style={{ fontSize: '0.875rem', color: 'var(--primary-700)' }}>
                        💡 Las plantillas usan variables dinámicas como <code style={{ background: 'white', padding: '2px 6px', borderRadius: '4px' }}>{"{{contacto_nombre}}"}</code> que se reemplazan automáticamente al enviar recordatorios.
                    </p>
                </div>
            </div>

            {/* Grid de plantillas */}
            {plantillas.length === 0 ? (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-state-icon">📝</div>
                        <div className="empty-state-title">Sin plantillas personalizadas</div>
                        <p className="empty-state-text">Crea plantillas para tus recordatorios por email y Telegram</p>
                        <button className="btn btn-primary" onClick={() => openModal()}>
                            + Nueva Plantilla
                        </button>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '16px' }}>
                    {plantillas.map((plantilla) => (
                        <div key={plantilla.id} className="card">
                            <div className="card-header">
                                <div>
                                    <span className={`badge badge-${plantilla.tipo === 'email' ? 'primary' : 'success'}`} style={{ marginRight: '8px' }}>
                                        {plantilla.tipo === 'email' ? '📧 Email' : '📱 Telegram'}
                                    </span>
                                    {plantilla.es_default && (
                                        <span className="badge badge-warning">⭐ Default</span>
                                    )}
                                </div>
                            </div>
                            <div className="card-body">
                                <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '8px' }}>
                                    {plantilla.nombre}
                                </h3>
                                {plantilla.asunto && (
                                    <p style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '8px' }}>
                                        <strong>Asunto:</strong> {plantilla.asunto}
                                    </p>
                                )}
                                <p style={{ fontSize: '0.8rem', color: 'var(--gray-500)', whiteSpace: 'pre-wrap', maxHeight: '100px', overflow: 'hidden' }}>
                                    {plantilla.mensaje.slice(0, 150)}...
                                </p>
                                <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                                    <button className="btn btn-sm btn-secondary" onClick={() => handlePreview(plantilla)}>
                                        👁 Preview
                                    </button>
                                    <button className="btn btn-sm btn-secondary" onClick={() => openModal(plantilla)}>
                                        ✏️ Editar
                                    </button>
                                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(plantilla.id)}>
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal Crear/Editar */}
            {showModal && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal" style={{ maxWidth: '600px' }} onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">
                                {editingPlantilla ? 'Editar Plantilla' : 'Nueva Plantilla'}
                            </h2>
                            <button className="modal-close" onClick={closeModal}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
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
                                        <label className="form-label">Tipo *</label>
                                        <select
                                            className="form-select"
                                            value={formData.tipo}
                                            onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                                        >
                                            <option value="telegram">📱 Telegram</option>
                                            <option value="email">📧 Email</option>
                                        </select>
                                    </div>
                                </div>

                                {formData.tipo === 'email' && (
                                    <div className="form-group">
                                        <label className="form-label">Asunto del Email</label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            value={formData.asunto}
                                            onChange={(e) => setFormData({ ...formData, asunto: e.target.value })}
                                            placeholder="Recordatorio: {{titulo}}"
                                        />
                                    </div>
                                )}

                                <div className="form-group">
                                    <label className="form-label">Mensaje *</label>
                                    <textarea
                                        className="form-textarea"
                                        value={formData.mensaje}
                                        onChange={(e) => setFormData({ ...formData, mensaje: e.target.value })}
                                        rows="6"
                                        required
                                        placeholder="Hola {{contacto_nombre}}, te recuerdo sobre..."
                                    />
                                </div>

                                {/* Variables disponibles */}
                                <div style={{ marginBottom: '16px' }}>
                                    <label className="form-label">Variables disponibles (click para insertar):</label>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                        {variablesDisponibles.map((v) => (
                                            <button
                                                key={v.nombre}
                                                type="button"
                                                className="btn btn-sm btn-secondary"
                                                onClick={() => insertVariable(v.nombre)}
                                                title={v.desc}
                                            >
                                                {`{{${v.nombre}}}`}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                        <input
                                            type="checkbox"
                                            checked={formData.es_default}
                                            onChange={(e) => setFormData({ ...formData, es_default: e.target.checked })}
                                        />
                                        <span className="form-label" style={{ margin: 0 }}>Usar como plantilla por defecto</span>
                                    </label>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    {editingPlantilla ? 'Guardar' : 'Crear Plantilla'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal Preview */}
            {showPreview && previewContent && (
                <div className="modal-overlay" onClick={() => setShowPreview(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">👁 Preview: {previewContent.plantilla.nombre}</h2>
                            <button className="modal-close" onClick={() => setShowPreview(false)}>&times;</button>
                        </div>
                        <div className="modal-body">
                            {previewContent.asunto && (
                                <div style={{ marginBottom: '16px' }}>
                                    <strong>Asunto:</strong>
                                    <div style={{ padding: '12px', background: 'var(--gray-100)', borderRadius: '8px', marginTop: '8px' }}>
                                        {previewContent.asunto}
                                    </div>
                                </div>
                            )}
                            <div>
                                <strong>Mensaje:</strong>
                                <div style={{ padding: '12px', background: 'var(--gray-100)', borderRadius: '8px', marginTop: '8px', whiteSpace: 'pre-wrap' }}>
                                    {previewContent.mensaje}
                                </div>
                            </div>
                            <p style={{ fontSize: '0.75rem', color: 'var(--gray-400)', marginTop: '16px' }}>
                                * Preview con datos de ejemplo
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Plantillas;
