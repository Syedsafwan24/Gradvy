/**
 * Cookie utility functions for Gradvy frontend
 * Handles CSRF token retrieval and other cookie operations
 */

/**
 * Get CSRF token from cookies
 * @returns {string} CSRF token value or empty string if not found
 */
export const getCSRFToken = () => {
  if (typeof document === 'undefined') {
    // Server-side rendering case
    return '';
  }
  
  const cookieMatch = document.cookie.match(/csrftoken=([^;]*)/);
  return cookieMatch ? cookieMatch[1] : '';
};

/**
 * Get a specific cookie value by name
 * @param {string} name - Cookie name
 * @returns {string} Cookie value or empty string if not found
 */
export const getCookie = (name) => {
  if (typeof document === 'undefined') {
    return '';
  }
  
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return '';
};

/**
 * Set a cookie
 * @param {string} name - Cookie name
 * @param {string} value - Cookie value
 * @param {number} days - Expiration in days (optional)
 * @param {string} path - Cookie path (default: '/')
 */
export const setCookie = (name, value, days, path = '/') => {
  if (typeof document === 'undefined') {
    return;
  }
  
  let expires = '';
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = '; expires=' + date.toUTCString();
  }
  
  document.cookie = `${name}=${value}${expires}; path=${path}`;
};

/**
 * Delete a cookie
 * @param {string} name - Cookie name to delete
 * @param {string} path - Cookie path (default: '/')
 */
export const deleteCookie = (name, path = '/') => {
  if (typeof document === 'undefined') {
    return;
  }
  
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${path};`;
};

/**
 * Check if cookies are enabled
 * @returns {boolean} True if cookies are enabled
 */
export const areCookiesEnabled = () => {
  if (typeof document === 'undefined') {
    return false;
  }
  
  try {
    document.cookie = 'test_cookie=test';
    const enabled = document.cookie.indexOf('test_cookie=test') !== -1;
    document.cookie = 'test_cookie=; expires=Thu, 01 Jan 1970 00:00:00 UTC';
    return enabled;
  } catch (e) {
    return false;
  }
};