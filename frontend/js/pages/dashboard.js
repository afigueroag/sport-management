/* ============================================
   DASHBOARD - Página de control principal
   ============================================ */

import * as auth from '../auth.js';

/**
 * Obtiene las características por rol
 */
function getFeaturesByRole(role) {
  const features = {
    admin: [
      'Ver KPIs y métricas (ingresos, estudiantes activos)',
      'Gestionar estudiantes',
      'Gestionar clases y horarios',
      'Ver reportes de asistencia',
      'Gestionar pagos y membresías',
      'Enviar recordatorios de pago',
    ],
    instructor: [
      'Ver mis clases asignadas',
      'Marcar asistencia por clase',
      'Ver historial de asistencia',
      'Añadir notas sobre estudiantes',
      'Solicitar cambios de horario',
    ],
    student: [
      'Ver mis clases inscritas',
      'Inscribirme en nuevas clases',
      'Ver mi estado de pago',
      'Ver historial de asistencia',
      'Gestionar mi membresía',
    ],
    receptionist: [
      'Inscribir nuevos estudiantes',
      'Registrar pagos manuales',
      'Ver lista de estudiantes',
      'Enviar recordatorios de pago',
    ],
  };

  return features[role] || [];
}

/**
 * Cargar datos del usuario actual
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

    // Mostrar información del usuario
    document.getElementById('user-name').textContent = user.full_name || user.email;
    document.getElementById('user-email').textContent = user.email;

    // Mostrar rol
    const roleElement = document.getElementById('user-role');
    roleElement.textContent = formatRole(user.role);
    roleElement.className = `badge badge-${getBadgeColor(user.role)}`;

    // Cargar características por rol
    loadFeaturesByRole(user.role);

    console.log('✓ User data loaded:', user);
  } catch (error) {
    console.error('Error loading user data:', error);
    document.getElementById('user-name').textContent = 'Error';
    document.getElementById('user-email').textContent = 'Error al cargar datos';
  }
}

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
function getBadgeColor(role) {
  const colors = {
    admin: 'primary',
    instructor: 'success',
    student: 'secondary',
    receptionist: 'warning',
  };
  return colors[role] || 'secondary';
}

/**
 * Carga las características según el rol
 */
function loadFeaturesByRole(role) {
  const features = getFeaturesByRole(role);
  const container = document.getElementById('features-by-role');

  if (features.length === 0) {
    container.innerHTML = '<p style="color: var(--text-tertiary);">No hay características disponibles.</p>';
    return;
  }

  const html = `
    <p style="color: var(--text-secondary); margin-bottom: var(--spacing-4);">
      Como <strong>${formatRole(role)}</strong>, tendrás acceso a:
    </p>
    <ul style="list-style-type: disc; padding-left: var(--spacing-6);">
      ${features.map((feature) => `<li style="margin-bottom: var(--spacing-2);">${feature}</li>`).join('')}
    </ul>
  `;

  container.innerHTML = html;
}

/**
 * Maneja el logout
 */
function handleLogout() {
  auth.logout();
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

  // Event listeners
  document.getElementById('logout-btn').addEventListener('click', handleLogout);

  // Inicializar auto-refresh de tokens
  auth.initTokenRefreshInterceptor();

  console.log('✓ Dashboard initialized');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);
