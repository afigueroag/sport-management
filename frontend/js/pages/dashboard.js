/* ============================================
   DASHBOARD - Página de control principal con vistas por rol
   ============================================ */

import * as auth from '../auth.js';

/**
 * Formatea el nombre del rol
 */
function formatRole(role) {
  const roleNames = {
    admin: 'Administrador',
    instructor: 'Instructor',
    student: 'Estudiante',
    receptionist: 'Recepcionista',
  };
  return roleNames[role] || role;
}

/**
 * Retorna el color del badge según el rol
 */
function getRoleBadgeClass(role) {
  const classes = {
    admin: 'badge-role admin',
    instructor: 'badge-role instructor',
    student: 'badge-role student',
    receptionist: 'badge-role receptionist',
  };
  return classes[role] || 'badge-role';
}

/**
 * Muestra el dashboard apropiado según el rol
 */
function showDashboardByRole(role) {
  // Ocultar todos los dashboards
  document.getElementById('admin-dashboard')?.style.setProperty('display', 'none');
  document.getElementById('instructor-dashboard')?.style.setProperty('display', 'none');
  document.getElementById('student-dashboard')?.style.setProperty('display', 'none');

  // Mostrar el dashboard correspondiente
  const dashboardId = `${role}-dashboard`;
  const dashboard = document.getElementById(dashboardId);

  if (dashboard) {
    dashboard.style.setProperty('display', 'block');
  } else {
    console.warn(`Dashboard no encontrado para rol: ${role}`);
  }
}

/**
 * Carga datos del usuario actual y muestra el dashboard apropiado
 */
async function loadUserData() {
  try {
    const user = auth.getCurrentUser();

    if (!user) {
      // Si no hay usuario pero está autenticado, intenta obtenerlo del servidor
      await auth.fetchCurrentUser();
      location.reload();
      return;
    }

    // Mostrar información del usuario en navbar
    document.getElementById('user-name').textContent = user.full_name || user.email;

    const roleBadgeElement = document.getElementById('user-role-badge');
    roleBadgeElement.textContent = formatRole(user.role);
    roleBadgeElement.className = getRoleBadgeClass(user.role);

    // Mostrar el dashboard apropiado
    showDashboardByRole(user.role);

    // Cargar datos específicos del rol (si es necesario)
    loadRoleSpecificData(user.role);

    console.log('✓ User data loaded:', user);
  } catch (error) {
    console.error('Error loading user data:', error);
    document.getElementById('user-name').textContent = 'Error';
  }
}

/**
 * Carga datos específicos según el rol
 */
async function loadRoleSpecificData(role) {
  switch (role) {
    case 'admin':
      await loadAdminData();
      break;
    case 'instructor':
      await loadInstructorData();
      break;
    case 'student':
      await loadStudentData();
      break;
    case 'receptionist':
      // Receptionist dashboard coming in Phase 3+
      break;
  }
}

/**
 * Carga datos para dashboard admin
 */
async function loadAdminData() {
  try {
    // TODO: En Phase 5, conectar con API para traer datos reales
    // Por ahora, usamos datos mock

    // Los datos ya están en el HTML como placeholders
    console.log('✓ Admin data loaded (mock)');
  } catch (error) {
    console.error('Error loading admin data:', error);
  }
}

/**
 * Carga datos para dashboard instructor
 */
async function loadInstructorData() {
  try {
    // TODO: En Phase 5, conectar con API para traer:
    // - Clases asignadas para hoy
    // - Horario del instructor
    // - Estudiantes por clase

    // Por ahora, usamos datos mock en el HTML
    console.log('✓ Instructor data loaded (mock)');
  } catch (error) {
    console.error('Error loading instructor data:', error);
  }
}

/**
 * Carga datos para dashboard estudiante
 */
async function loadStudentData() {
  try {
    // TODO: En Phase 5, conectar con API para traer:
    // - Membresía actual del estudiante
    // - Clases inscritas
    // - Clases disponibles
    // - Historial de pagos

    // Por ahora, usamos datos mock en el HTML
    console.log('✓ Student data loaded (mock)');
  } catch (error) {
    console.error('Error loading student data:', error);
  }
}

/**
 * Maneja el logout
 */
function handleLogout() {
  auth.logout();
}

/**
 * Inicializa event listeners del dashboard
 */
function initializeEventListeners() {
  // Logout button
  document.getElementById('logout-btn').addEventListener('click', handleLogout);

  // TODO: En Phase 5, agregar listeners para:
  // - Botones "Marcar Asistencia"
  // - Botones "Inscribirme" en clases
  // - Botones "Recordatorio" de pago
  // - Etc.
}

/**
 * Inicializa la página
 */
function init() {
  // Proteger ruta: si no está autenticado, redirigir a login
  if (!auth.protectRoute()) {
    return;
  }

  loadUserData();
  initializeEventListeners();

  // Inicializar auto-refresh de tokens
  auth.initTokenRefreshInterceptor();

  console.log('✓ Dashboard initialized');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);
