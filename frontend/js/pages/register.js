/* ============================================
   REGISTER PAGE - Registro de nuevos usuarios
   ============================================ */

import api from '../api.js';
import * as auth from '../auth.js';

const form = document.getElementById('register-form');
const fullNameInput = document.getElementById('full-name');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const passwordConfirmInput = document.getElementById('password-confirm');
const termsCheckbox = document.getElementById('terms');
const submitBtn = document.getElementById('submit-btn');
const googleBtn = document.getElementById('google-btn');
const alertContainer = document.getElementById('alert-container');

// Validaciones
const validations = {
  fullName: {
    min: 2,
    max: 100,
    regex: /^[a-zA-Záéíóúñ\s]+$/,
  },
  email: {
    regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  password: {
    min: 8,
    regex: /^(?=.*[a-zA-Z])(?=.*\d)/, // Al menos una letra y un número
  },
};

/**
 * Limpia los errores de validación
 */
function clearErrors() {
  document.querySelectorAll('.input-error').forEach((el) => {
    el.textContent = '';
  });
  document.querySelectorAll('.input-group').forEach((el) => {
    el.classList.remove('has-error');
  });
}

/**
 * Muestra un error en el campo
 */
function showFieldError(fieldId, message) {
  const errorElement = document.getElementById(`${fieldId}-error`);
  if (errorElement) {
    errorElement.textContent = message;
  }
  const input = document.getElementById(fieldId);
  const inputGroup = input?.closest('.input-group');
  if (inputGroup) {
    inputGroup.classList.add('has-error');
  }
}

/**
 * Muestra una alerta
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

  // Auto-eliminar después de 5 segundos (solo para success/error)
  if (type !== 'info') {
    setTimeout(() => alertElement.remove(), 5000);
  }
}

/**
 * Valida el nombre completo
 */
function validateFullName(name) {
  const trimmed = name.trim();

  if (!trimmed) {
    return 'El nombre es requerido';
  }

  if (trimmed.length < validations.fullName.min) {
    return `El nombre debe tener al menos ${validations.fullName.min} caracteres`;
  }

  if (trimmed.length > validations.fullName.max) {
    return `El nombre no puede exceder ${validations.fullName.max} caracteres`;
  }

  return null;
}

/**
 * Valida el email
 */
function validateEmail(email) {
  const trimmed = email.trim().toLowerCase();

  if (!trimmed) {
    return 'El email es requerido';
  }

  if (!validations.email.regex.test(trimmed)) {
    return 'Por favor ingresa un email válido';
  }

  return null;
}

/**
 * Valida la contraseña
 */
function validatePassword(password) {
  if (!password) {
    return 'La contraseña es requerida';
  }

  if (password.length < validations.password.min) {
    return `La contraseña debe tener al menos ${validations.password.min} caracteres`;
  }

  if (!validations.password.regex.test(password)) {
    return 'La contraseña debe incluir letras y números';
  }

  return null;
}

/**
 * Valida la confirmación de contraseña
 */
function validatePasswordConfirm(password, passwordConfirm) {
  if (!passwordConfirm) {
    return 'Debes confirmar tu contraseña';
  }

  if (password !== passwordConfirm) {
    return 'Las contraseñas no coinciden';
  }

  return null;
}

/**
 * Valida términos y condiciones
 */
function validateTerms(isChecked) {
  if (!isChecked) {
    return 'Debes aceptar los términos y condiciones';
  }

  return null;
}

/**
 * Valida todo el formulario
 */
function validateForm() {
  clearErrors();
  let isValid = true;

  const fullNameError = validateFullName(fullNameInput.value);
  if (fullNameError) {
    showFieldError('full-name', fullNameError);
    isValid = false;
  }

  const emailError = validateEmail(emailInput.value);
  if (emailError) {
    showFieldError('email', emailError);
    isValid = false;
  }

  const passwordError = validatePassword(passwordInput.value);
  if (passwordError) {
    showFieldError('password', passwordError);
    isValid = false;
  }

  const passwordConfirmError = validatePasswordConfirm(
    passwordInput.value,
    passwordConfirmInput.value
  );
  if (passwordConfirmError) {
    showFieldError('password-confirm', passwordConfirmError);
    isValid = false;
  }

  const termsError = validateTerms(termsCheckbox.checked);
  if (termsError) {
    showFieldError('terms', termsError);
    isValid = false;
  }

  return isValid;
}

/**
 * Maneja el envío del formulario
 */
async function handleRegister(e) {
  e.preventDefault();

  if (!validateForm()) {
    return;
  }

  // Mostrar estado de carga
  submitBtn.disabled = true;
  const originalText = submitBtn.textContent;
  submitBtn.innerHTML = '<span class="spinner"></span> Creando cuenta...';

  try {
    const fullName = fullNameInput.value.trim();
    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    // Llamar al API de registro
    const user = await auth.register(email, password, fullName);

    // Registro exitoso
    showAlert(`¡Bienvenido, ${user.full_name}! Tu cuenta ha sido creada.`, 'success');

    // Redirigir al dashboard después de 2 segundos
    setTimeout(() => {
      window.location.href = '/dashboard.html';
    }, 2000);
  } catch (error) {
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;

    console.error('Register error:', error.message);

    // Manejar errores específicos
    if (error.message.includes('already exists') || error.message.includes('409')) {
      showFieldError('email', 'Este email ya está registrado. ¿Quizás debas iniciar sesión?');
      showAlert('Este email ya tiene una cuenta en nuestro sistema', 'error');
    } else if (error.message.includes('validation')) {
      showAlert('Hay errores en tu información. Por favor revisa los campos.', 'error');
    } else {
      showAlert(`Error al crear cuenta: ${error.message}`, 'error');
    }
  }
}

/**
 * Maneja Google login (placeholder para Phase 2+)
 */
function handleGoogleRegister(e) {
  e.preventDefault();
  showAlert('Registro con Google será implementado en una fase posterior', 'info');
  // TODO: Implementar OAuth con Google
}

/**
 * Valida en tiempo real
 */
function setupRealTimeValidation() {
  fullNameInput.addEventListener('blur', () => {
    const error = validateFullName(fullNameInput.value);
    if (error) {
      showFieldError('full-name', error);
    } else {
      document.getElementById('full-name-error').textContent = '';
      fullNameInput.closest('.input-group')?.classList.remove('has-error');
    }
  });

  emailInput.addEventListener('blur', () => {
    const error = validateEmail(emailInput.value);
    if (error) {
      showFieldError('email', error);
    } else {
      document.getElementById('email-error').textContent = '';
      emailInput.closest('.input-group')?.classList.remove('has-error');
    }
  });

  passwordInput.addEventListener('blur', () => {
    const error = validatePassword(passwordInput.value);
    if (error) {
      showFieldError('password', error);
    } else {
      document.getElementById('password-error').textContent = '';
      passwordInput.closest('.input-group')?.classList.remove('has-error');
    }
  });

  passwordConfirmInput.addEventListener('blur', () => {
    const error = validatePasswordConfirm(passwordInput.value, passwordConfirmInput.value);
    if (error) {
      showFieldError('password-confirm', error);
    } else {
      document.getElementById('password-confirm-error').textContent = '';
      passwordConfirmInput.closest('.input-group')?.classList.remove('has-error');
    }
  });

  termsCheckbox.addEventListener('change', () => {
    if (termsCheckbox.checked) {
      document.getElementById('terms-error').textContent = '';
      termsCheckbox.closest('.checkbox')?.classList.remove('has-error');
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

  setupRealTimeValidation();

  form.addEventListener('submit', handleRegister);
  googleBtn.addEventListener('click', handleGoogleRegister);

  // Focus en nombre al cargar
  fullNameInput.focus();

  console.log('✓ Register page initialized');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', init);
