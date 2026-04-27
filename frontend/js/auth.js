/* ============================================
   AUTH - Gestión de autenticación y tokens JWT
   ============================================ */

import api from './api.js';

const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

/**
 * Obtiene el token de acceso
 */
export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Obtiene el token de refresco
 */
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Obtiene el usuario actual
 */
export function getCurrentUser() {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
}

/**
 * Verifica si el usuario está autenticado
 */
export function isAuthenticated() {
  return !!getAccessToken();
}

/**
 * Guarda los tokens después de login/register
 */
export function saveTokens(accessToken, refreshToken, user = null) {
  localStorage.setItem(TOKEN_KEY, accessToken);

  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }

  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Limpia los tokens y usuario
 */
export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Realiza login con email y contraseña
 */
export async function login(email, password) {
  try {
    const response = await api.auth.login(email, password);

    saveTokens(
      response.access_token,
      response.refresh_token,
      response.user
    );

    return response.user;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

/**
 * Realiza registro de usuario
 */
export async function register(email, password, fullName) {
  try {
    const response = await api.auth.register(email, password, fullName);

    saveTokens(
      response.access_token,
      response.refresh_token,
      response.user
    );

    return response.user;
  } catch (error) {
    console.error('Register error:', error);
    throw error;
  }
}

/**
 * Realiza logout
 */
export async function logout() {
  try {
    await api.auth.logout();
  } catch (error) {
    console.warn('Logout error:', error);
  } finally {
    clearTokens();
    window.location.href = '/';
  }
}

/**
 * Refresca el token de acceso
 */
export async function refreshAccessToken() {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    clearTokens();
    return null;
  }

  try {
    const response = await api.auth.refreshToken(refreshToken);
    saveTokens(response.access_token, response.refresh_token);
    return response.access_token;
  } catch (error) {
    console.error('Token refresh error:', error);
    clearTokens();
    window.location.href = '/login.html';
    return null;
  }
}

/**
 * Obtiene el usuario actual desde el servidor
 */
export async function fetchCurrentUser() {
  try {
    const user = await api.auth.me();
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    return user;
  } catch (error) {
    clearTokens();
    throw error;
  }
}

/**
 * Decodifica un JWT (sin validación de firma)
 * Nota: Esto es solo para leer el payload, la validación se hace en el servidor
 */
export function decodeToken(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const decoded = JSON.parse(atob(parts[1]));
    return decoded;
  } catch (error) {
    console.error('Token decode error:', error);
    return null;
  }
}

/**
 * Verifica si el token está cerca de expirar (< 5 minutos)
 */
export function isTokenExpiringSoon() {
  const token = getAccessToken();
  if (!token) return true;

  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;

  const expiresIn = decoded.exp * 1000 - Date.now();
  return expiresIn < 5 * 60 * 1000; // 5 minutos
}

/**
 * Solicita restablecimiento de contraseña
 */
export async function forgotPassword(email) {
  try {
    return await api.auth.forgotPassword(email);
  } catch (error) {
    console.error('Forgot password error:', error);
    throw error;
  }
}

/**
 * Restablece contraseña con token
 */
export async function resetPassword(token, password) {
  try {
    return await api.auth.resetPassword(token, password);
  } catch (error) {
    console.error('Reset password error:', error);
    throw error;
  }
}

/**
 * Protege una ruta: redirige a login si no está autenticado
 */
export function protectRoute() {
  if (!isAuthenticated()) {
    window.location.href = '/login.html';
    return false;
  }

  // Verificar si el token está por expirar
  if (isTokenExpiringSoon()) {
    refreshAccessToken();
  }

  return true;
}

/**
 * Inicializa el interceptor de renovación automática de tokens
 */
export function initTokenRefreshInterceptor() {
  setInterval(() => {
    if (isAuthenticated() && isTokenExpiringSoon()) {
      refreshAccessToken();
    }
  }, 60000); // Verificar cada minuto
}

export default {
  getAccessToken,
  getRefreshToken,
  getCurrentUser,
  isAuthenticated,
  saveTokens,
  clearTokens,
  login,
  register,
  logout,
  refreshAccessToken,
  fetchCurrentUser,
  decodeToken,
  isTokenExpiringSoon,
  forgotPassword,
  resetPassword,
  protectRoute,
  initTokenRefreshInterceptor,
};
