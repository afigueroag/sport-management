/* ============================================
   API - Wrapper de fetch para comunicación con backend
   ============================================ */

const API_BASE_URL = import.meta?.env?.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Realiza una solicitud GET
 */
export async function get(endpoint, options = {}) {
  return request('GET', endpoint, null, options);
}

/**
 * Realiza una solicitud POST
 */
export async function post(endpoint, data, options = {}) {
  return request('POST', endpoint, data, options);
}

/**
 * Realiza una solicitud PUT
 */
export async function put(endpoint, data, options = {}) {
  return request('PUT', endpoint, data, options);
}

/**
 * Realiza una solicitud PATCH
 */
export async function patch(endpoint, data, options = {}) {
  return request('PATCH', endpoint, data, options);
}

/**
 * Realiza una solicitud DELETE
 */
export async function remove(endpoint, options = {}) {
  return request('DELETE', endpoint, null, options);
}

/**
 * Realiza una solicitud HTTP genérica
 */
async function request(method, endpoint, data = null, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('access_token');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Agregar token JWT si está disponible
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
    ...options,
  };

  // Agregar body si es necesario
  if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);

    // Manejo de errores de autenticación
    if (response.status === 401) {
      // Token expirado, intentar refrescar o redirigir a login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login.html';
      return;
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `HTTP ${response.status}`,
      }));
      throw new Error(error.message || error.detail);
    }

    // Retornar respuesta JSON o vacía
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return null;
  } catch (error) {
    console.error(`API Error [${method} ${endpoint}]:`, error.message);
    throw error;
  }
}

/**
 * Endpoints de autenticación
 */
export const auth = {
  login: (email, password) => post('/auth/login', { email, password }),
  register: (email, password, full_name) =>
    post('/auth/register', { email, password, full_name }),
  logout: () => post('/auth/logout', {}),
  refreshToken: (refreshToken) =>
    post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => get('/auth/me'),
  forgotPassword: (email) => post('/auth/forgot-password', { email }),
  resetPassword: (token, password) =>
    post('/auth/reset-password', { token, password }),
};

/**
 * Endpoints de estudiantes
 */
export const students = {
  list: (params) => get('/students', { search: params }),
  get: (id) => get(`/students/${id}`),
  create: (data) => post('/students', data),
  update: (id, data) => put(`/students/${id}`, data),
  delete: (id) => remove(`/students/${id}`),
  getAttendance: (id) => get(`/students/${id}/attendance`),
};

/**
 * Endpoints de clases
 */
export const classes = {
  list: (params) => get('/classes', { search: params }),
  get: (id) => get(`/classes/${id}`),
  create: (data) => post('/classes', data),
  update: (id, data) => put(`/classes/${id}`, data),
  delete: (id) => remove(`/classes/${id}`),
  getSessions: (id) => get(`/classes/${id}/sessions`),
  enrollStudent: (classId, studentId) =>
    post(`/classes/${classId}/enroll`, { student_id: studentId }),
  unenrollStudent: (classId, studentId) =>
    remove(`/classes/${classId}/unenroll/${studentId}`),
};

/**
 * Endpoints de asistencia
 */
export const attendance = {
  list: (params) => get('/attendance', { search: params }),
  create: (data) => post('/attendance', data),
  update: (id, data) => put(`/attendance/${id}`, data),
  delete: (id) => remove(`/attendance/${id}`),
  getByClass: (classId) => get(`/attendance/class/${classId}`),
  getByStudent: (studentId) => get(`/attendance/student/${studentId}`),
};

/**
 * Endpoints de pagos
 */
export const payments = {
  list: (params) => get('/payments', { search: params }),
  get: (id) => get(`/payments/${id}`),
  getPlans: () => get('/payments/plans'),
  createCheckoutSession: (data) => post('/payments/checkout', data),
  getInvoices: (studentId) => get(`/payments/invoices/${studentId}`),
  webhook: (data) => post('/payments/webhook', data),
};

/**
 * Endpoints de reportes
 */
export const reports = {
  summary: () => get('/reports/summary'),
  attendance: (params) => get('/reports/attendance', { search: params }),
  revenue: (params) => get('/reports/revenue', { search: params }),
  students: (params) => get('/reports/students', { search: params }),
};

/**
 * Endpoints de dashboard
 */
export const dashboard = {
  adminSummary: () => get('/dashboard/admin/summary'),
  instructorSummary: () => get('/dashboard/instructor/summary'),
  studentSummary: () => get('/dashboard/student/summary'),
};

/**
 * Endpoints de class sessions
 */
export const classSessions = {
  list: (classId) => get(`/class-sessions?class_id=${classId}`),
  get: (id) => get(`/class-sessions/${id}`),
  create: (data) => post('/class-sessions', data),
  update: (id, data) => put(`/class-sessions/${id}`, data),
  delete: (id) => remove(`/class-sessions/${id}`),
};

/**
 * Endpoints de inscripciones
 */
export const enrollments = {
  list: (params) => get('/enrollments', { search: params }),
  get: (id) => get(`/enrollments/${id}`),
  create: (data) => post('/enrollments', data),
  update: (id, data) => put(`/enrollments/${id}`, data),
  delete: (id) => remove(`/enrollments/${id}`),
};

export default {
  get,
  post,
  put,
  patch,
  remove,
  auth,
  students,
  classes,
  classSessions,
  enrollments,
  attendance,
  payments,
  reports,
  dashboard,
};
