/* ============================================
   LOGIN PAGE - Autenticación de usuario
   ============================================ */

import api from '../api.js';
import * as auth from '../auth.js';

const form = document.getElementById('login-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const rememberMeCheckbox = document.getElementById('remember-me');
const submitBtn = document.getElementById('submit-btn');
const googleBtn = document.getElementById('google-btn');
const alertContainer = document.getElementById('alert-container');

/**
 * Valida un email
 */
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Limpia los errores de validación
 */
function clearErrors() {
  document.getElementById('email-error').textContent = '';
  document.getElementById('password-error').textContent = '';
  document.querySelector('.input-group[data-field="email"]')?.classList.remove('has-error');
  document.querySelector('.input-group[data-field="password"]')?.classList.remove('has-error');
}

/**
 * Muestra un error en el campo
 */
function showFieldError(fieldId, message) {
  const errorElement = document.getElementById(`${fieldId}-error`);
  if (errorElement) {
    errorElement.textContent = message;
  }
  const inputGroup = document.getElementById(fieldId).closest('.input-group');
  if (inputGroup) {
    inputGroup.classList.add('has-error');
  }
}

/**
 * Muestra una alerta en la parte superior
 */
function showAlert(message, type = 'info') {
  const alertClass = `alert alert-${type}`;
  const alertElement = document.createElement('div');
  alertElement.className = alertClass;
  alertElement.innerHTML = `
    <div style="flex: 1;">${message}</div>
    <button class="alert-close" aria-label="Cerrar">&times;</button>
  `;

  alertContainer.innerHTML = '';
  alertContainer.appendChild(alertElement);

  alertElement.querySelector('.alert-close').addEventListener('click', () => {
    alertElement.remove();
  });

  // Auto-eliminar después de 5 segundos (solo para success/error, no para info)
  if (type !== 'info') {
    setTimeout(() => alertElement.remove(), 5000);
  }
}

/**
 * Valida el formulario
 */
function validateForm() {
  clearErrors();
  let isValid = true;

  // Validar email
  const email = emailInput.value.trim();
  if (!email) {
    showFieldError('email', 'El email es requerido');
    isValid = false;
  } else if (!isValidEmail(email)) {
    showFieldError('email', 'Por favor ingresa un email válido');
    isValid = false;
  }

  // Validar contraseña
  const password = passwordInput.value;
  if (!password) {
    showFieldError('password', 'La contraseña es requerida');
    isValid = false;
  } else if (password.length < 6) {
    showFieldError('password', 'La contraseña debe tener al menos 6 caracteres');
    isValid = false;
  }

  return isValid;
}

/**
 * Maneja el envío del formulario
 */
async function handleLogin(e) {
  e.preventDefault();

  if (!validateForm()) {
    return;
  }

  // Mostrar estado de carga
  submitBtn.disabled = true;
  const originalText = submitBtn.textContent;
  submitBtn.innerHTML = '<span class="spinner"></span> Iniciando sesión...';

  try {
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Llamar al API
    const user = await auth.login(email, password);

    // Login exitoso
    showAlert(`¡Bienvenido, ${user.full_name}!`, 'success');

    // Guardar preferencia "Recuérdame" (opcional)
    if (rememberMeCheckbox.checked) {
      localStorage.setItem('remember_email', email);
    }

    // Redirigir al dashboard después de 1 segundo
    setTimeout(() => {
      const redirect = new URLSearchParams(window.location.search).get('redirect');
      window.location.href = redirect || '/dashboard.html';
    }, 1000);
  } catch (error) {
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;

    console.error('Login error:', error.message);

    // Mostrar error
    if (error.message.includes('401') || error.message.includes('Invalid credentials')) {
      showAlert('Email o contraseña incorrectos', 'error');
    } else if (error.message.includes('404')) {
      showAlert('Usuario no encontrado. ¿Quizás debas registrarte?', 'error');
    } else {
      showAlert(`Error: ${error.message}`, 'error');
    }
  }
}

/**
 * Maneja Google login (placeholder para Phase 2+)
 */
function handleGoogleLogin(e) {
  e.preventDefault();
  showAlert('Google login será implementado en una fase posterior', 'info');
  // TODO: Implementar OAuth con Google
}

/**
 * Carga el email guardado si "Recuérdame" fue activado
 */
function loadRememberedEmail() {
  const rememberedEmail = localStorage.getItem('remember_email');
  if (rememberedEmail) {
    emailInput.value = rememberedEmail;
    rememberMeCheckbox.checked = true;
  }
}

/**
 * Valida en tiempo real
 */
function setupRealTimeValidation() {
  emailInput.addEventListener('blur', () => {
    const email = emailInput.value.trim();
    if (email && !isValidEmail(email)) {
      showFieldError('email', 'Email inválido');
    } else {
      document.getElementById('email-error').textContent = '';
      emailInput.closest('.input-group')?.classList.remove('has-error');
    }
  });

  passwordInput.addEventListener('blur', () => {
    const password = passwordInput.value;
    if (password && password.length < 6) {
      showFieldError('password', 'Mínimo 6 caracteres');
    } else if (password) {
      document.getElementById('password-error').textContent = '';
      passwordInput.closest('.input-group')?.classList.remove('has-error');
    }
  });
}

/**
 * Inicializa la página
 */
function init() {
  // Si ya está autenticado, redirigir al dashboard
  if (auth.isAuthenticated()) {
    window.location.href = '/dashboard.html';
    return;
  }

  loadRememberedEmail();
  setupRealTimeValidation();

  form.addEventListener('submit', handleLogin);
  googleBtn.addEventListener('click', handleGoogleLogin);

  // Focus en email al cargar
  emailInput.focus();

  console.log('✓ Login page initialized');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);
