// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/config/api.js
// Centralized API configuration to avoid hardcoded URLs
// Provides environment-based API endpoints for development and production
// RELEVANT FILES: apiSlice.js, authApi.js, PrivacyQuickLinks.jsx, AuthInitializer.jsx

// Get the API base URL from environment variables or use defaults
const getApiBaseUrl = () => {
  // In production, this would come from environment variables
  // For now, keeping localhost for development but centralized
  if (typeof window !== 'undefined') {
    // Client-side: can access window.location
    const { protocol, hostname } = window.location;
    
    // Development detection
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.includes('dev')) {
      return 'http://localhost:8000';
    }
    
    // Production would use the same domain
    return `${protocol}//${hostname}`;
  } else {
    // Server-side rendering: use environment variable or default
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }
};

export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  API_BASE_URL: `${getApiBaseUrl()}/api/`,
  AUTH_BASE_URL: `${getApiBaseUrl()}/api/auth/`,
  
  // API endpoints
  ENDPOINTS: {
    // Auth endpoints
    LOGIN: 'auth/login/',
    LOGOUT: 'auth/logout/',
    REGISTER: 'auth/register/',
    REFRESH: 'auth/refresh/',
    
    // Preferences endpoints
    CONSENT_HISTORY_DOWNLOAD: 'preferences/consent-history/download/',
    CONSENT_REVOKE_ALL: 'preferences/consent/revoke-all/',
    
    // User endpoints
    USER_PROFILE: 'user/profile/',
    USER_PREFERENCES: 'preferences/',
  },
  
  // Request configuration
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  },
  
  // Timeout configuration
  TIMEOUT: 30000, // 30 seconds
};

export default API_CONFIG;