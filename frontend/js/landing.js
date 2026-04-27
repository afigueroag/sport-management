/* ============================================
   LANDING PAGE - Funcionalidad interactiva
   ============================================ */

/**
 * Desplaza hacia una sección específica
 */
function scrollToSection(sectionId) {
  const element = document.getElementById(sectionId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
}

/**
 * Inicia prueba gratuita
 */
function startFreeTrial() {
  // Mostrar alerta o redirigir a registro
  window.location.href = 'register.html?trial=true';
}

/**
 * Solicita demostración
 */
function requestDemo() {
  const modal = document.getElementById('demo-modal');
  const nameInput = modal.querySelector('input[placeholder*="nombre completo"]');
  const emailInput = modal.querySelector('input[type="email"]');
  const academyInput = modal.querySelector('input[placeholder*="Academia"]');
  const phoneInput = modal.querySelector('input[type="tel"]');

  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const academy = academyInput.value.trim();
  const phone = phoneInput.value.trim();

  // Validación básica
  if (!name || !email || !academy || !phone) {
    showAlert('Por favor completa todos los campos', 'error');
    return;
  }

  if (!isValidEmail(email)) {
    showAlert('Por favor ingresa un email válido', 'error');
    return;
  }

  // Aquí irá la integración con el backend
  console.log('Solicitud de demo:', { name, email, academy, phone });

  showAlert('¡Solicitud enviada! Nos pondremos en contacto pronto.', 'success');
  modal.classList.remove('active');

  // Limpiar formulario
  nameInput.value = '';
  emailInput.value = '';
  academyInput.value = '';
  phoneInput.value = '';
}

/**
 * Contacta con ventas
 */
function contactSales() {
  window.location.href = 'mailto:ventas@sportacademia.com?subject=Información%20Plan%20Empresarial';
}

/**
 * Valida formato de email
 */
function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Muestra alerta temporal
 */
function showAlert(message, type = 'info') {
  const alertClass = `alert alert-${type}`;

  const alertElement = document.createElement('div');
  alertElement.className = alertClass;
  alertElement.innerHTML = `
    <div style="flex: 1;">${message}</div>
    <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  document.body.insertAdjacentElement('afterbegin', alertElement);

  // Auto-eliminar después de 5 segundos
  setTimeout(() => {
    alertElement.remove();
  }, 5000);
}

/**
 * Navegación activa en navbar
 */
function initNavigation() {
  const navLinks = document.querySelectorAll('.navbar-nav-item a');

  window.addEventListener('scroll', () => {
    let current = '';

    document.querySelectorAll('section[id]').forEach((section) => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;

      if (scrollY >= sectionTop - 200) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove('active');
      if (link.getAttribute('href').slice(1) === current) {
        link.classList.add('active');
      }
    });
  });
}

/**
 * Efecto de scroll suave mejorado
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');

      if (href !== '#' && document.querySelector(href)) {
        e.preventDefault();
        document.querySelector(href).scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

/**
 * Animación de elementos en viewport
 */
function initIntersectionObserver() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px',
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observar tarjetas
  document.querySelectorAll('.feature-card, .sport-item, .pricing-card, .testimonial-card').forEach((el) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });
}

/**
 * Inicializar al cargar el DOM
 */
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSmoothScroll();
  initIntersectionObserver();

  console.log('✓ Landing page initialized');
});

/**
 * Manejo de modales
 */
document.addEventListener('click', (e) => {
  // Cerrar modal al hacer clic fuera del contenido
  if (e.target.classList.contains('modal')) {
    e.target.classList.remove('active');
  }

  // Cerrar modal con Escape
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      document.querySelectorAll('.modal.active').forEach((modal) => {
        modal.classList.remove('active');
      });
    }
  });
});
