/* ============================================
   DASHBOARD - Página de control principal con vistas por rol
   ============================================ */

import * as auth from '../auth.js';
import * as api from '../api.js';

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
    const data = await api.dashboard.adminSummary();

    // Actualizar métricas
    document.getElementById('admin-total-students').textContent = data.total_active_students || 0;
    document.getElementById('admin-monthly-sales').textContent = `$${(data.monthly_revenue || 0).toFixed(2)}`;

    // Cuentas por cobrar = suscripciones activas (as approximation)
    document.getElementById('admin-accounts-receivable').textContent =
      `${data.total_subscriptions || 0} activas`;

    console.log('✓ Admin data loaded:', data);
  } catch (error) {
    console.error('Error loading admin data:', error);
    document.getElementById('admin-total-students').textContent = '—';
    document.getElementById('admin-monthly-sales').textContent = '$—';
  }
}

/**
 * Carga datos para dashboard instructor
 */
async function loadInstructorData() {
  try {
    const data = await api.dashboard.instructorSummary();

    // Mostrar clases del instructor (placeholder - full implementation needed with class sessions)
    const classesToday = data.total_classes || 0;

    if (classesToday === 0) {
      document.getElementById('instructor-classes-today').innerHTML =
        '<p style="color: var(--text-secondary); padding: var(--spacing-3);">No tienes clases programadas para hoy.</p>';
    } else {
      // In a full implementation, we would fetch and display actual class sessions
      document.getElementById('instructor-classes-today').innerHTML =
        `<p style="color: var(--text-secondary); padding: var(--spacing-3);">Tienes ${classesToday} clase(s) asignada(s).</p>`;
    }

    console.log('✓ Instructor data loaded:', data);
  } catch (error) {
    console.error('Error loading instructor data:', error);
  }
}

/**
 * Carga datos para dashboard estudiante
 */
async function loadStudentData() {
  try {
    const data = await api.dashboard.studentSummary();

    // Mostrar información de membresía
    const subscriptionStatus = data.has_active_subscription ? 'Activa' : 'Sin membresía activa';
    const membershipCard = document.querySelector('.membership-status');
    if (membershipCard) {
      membershipCard.textContent = `Plan: ${data.subscription_type || 'N/A'} — ${subscriptionStatus}`;
    }

    // Mostrar clases inscritas
    const enrolledCount = data.enrolled_classes_count || 0;
    const enrollmentInfo = document.querySelector('.membership-date');
    if (enrollmentInfo) {
      enrollmentInfo.textContent = `Inscrito en ${enrolledCount} clase(s)`;
    }

    // Mostrar tasa de asistencia
    const attendanceRate = data.attendance_rate || 0;
    console.log(`Attendance rate: ${attendanceRate}%`);

    console.log('✓ Student data loaded:', data);
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
