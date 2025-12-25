/**
 * API Client - Conexión con el backend
 */

// En desarrollo usa proxy de Vite (/api), en producción usa la URL de Railway
const API_BASE = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api`
    : '/api';

// Obtener el telegram_id guardado
function getTelegramId() {
    return localStorage.getItem('telegram_id') || '';
}

// Headers comunes
function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'X-Telegram-ID': getTelegramId()
    };
}

// Fetch wrapper con manejo de errores
async function apiFetch(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            ...getHeaders(),
            ...options.headers
        }
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
        throw new Error(error.detail || 'Error en la solicitud');
    }

    return response.json();
}

// =============================================
// DASHBOARD
// =============================================
export async function getDashboard() {
    return apiFetch('/dashboard');
}

// =============================================
// CONTACTOS
// =============================================
export async function getContactos(search = '') {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    return apiFetch(`/contactos${params}`);
}

export async function getContacto(id) {
    return apiFetch(`/contactos/${id}`);
}

export async function createContacto(data) {
    return apiFetch('/contactos', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateContacto(id, data) {
    return apiFetch(`/contactos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function deleteContacto(id) {
    return apiFetch(`/contactos/${id}`, { method: 'DELETE' });
}

// =============================================
// TAREAS
// =============================================
export async function getTareas(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
    });
    const queryString = params.toString();
    return apiFetch(`/tareas${queryString ? `?${queryString}` : ''}`);
}

export async function getTareasKanban() {
    return apiFetch('/tareas/kanban');
}

export async function getTareasHoy() {
    return apiFetch('/tareas/hoy');
}

export async function getTarea(id) {
    return apiFetch(`/tareas/${id}`);
}

export async function createTarea(data) {
    return apiFetch('/tareas', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateTarea(id, data) {
    return apiFetch(`/tareas/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function cambiarEstadoTarea(id, estado) {
    return apiFetch(`/tareas/${id}/estado?estado=${estado}`, {
        method: 'PATCH'
    });
}

export async function deleteTarea(id) {
    return apiFetch(`/tareas/${id}`, { method: 'DELETE' });
}

// =============================================
// PROYECTOS
// =============================================
export async function getProyectos(estado = '') {
    const params = estado ? `?estado=${estado}` : '';
    return apiFetch(`/proyectos${params}`);
}

export async function getProyecto(id) {
    return apiFetch(`/proyectos/${id}`);
}

export async function createProyecto(data) {
    return apiFetch('/proyectos', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updateProyecto(id, data) {
    return apiFetch(`/proyectos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function deleteProyecto(id) {
    return apiFetch(`/proyectos/${id}`, { method: 'DELETE' });
}

// =============================================
// PLANTILLAS
// =============================================
export async function getPlantillas(tipo = '') {
    const params = tipo ? `?tipo=${tipo}` : '';
    return apiFetch(`/plantillas${params}`);
}

export async function getPlantilla(id) {
    return apiFetch(`/plantillas/${id}`);
}

export async function createPlantilla(data) {
    return apiFetch('/plantillas', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

export async function updatePlantilla(id, data) {
    return apiFetch(`/plantillas/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

export async function deletePlantilla(id) {
    return apiFetch(`/plantillas/${id}`, { method: 'DELETE' });
}

export async function previewPlantilla(id, variables = {}) {
    return apiFetch(`/plantillas/${id}/preview`, {
        method: 'POST',
        body: JSON.stringify(variables)
    });
}

// =============================================
// USUARIO
// =============================================
export async function getUsuario() {
    return apiFetch('/usuarios/me');
}

export async function updateUsuario(data) {
    return apiFetch('/usuarios/me', {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// =============================================
// UTILIDADES
// ==============================================
export function setTelegramId(id) {
    localStorage.setItem('telegram_id', id);
}

export function isLoggedIn() {
    return !!getTelegramId();
}

export function logout() {
    localStorage.removeItem('telegram_id');
}
