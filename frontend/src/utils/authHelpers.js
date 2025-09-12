// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/utils/authHelpers.js
// Centralized authentication helpers to replace direct localStorage access
// Provides secure token access through Redux store instead of localStorage
// RELEVANT FILES: authSlice.js, apiSlice.js, authApi.js, all preference components

import { store } from '@/store';
import { selectAuthTokens, selectCurrentUser, selectIsAuthenticated } from '@/store/slices/authSlice';

/**
 * Get authentication headers for API requests
 * Replaces direct localStorage.getItem('accessToken') calls
 * Uses Redux store as single source of truth for authentication
 */
export const getAuthHeaders = () => {
  const state = store.getState();
  const tokens = selectAuthTokens(state);
  const isAuthenticated = selectIsAuthenticated(state);
  
  if (!isAuthenticated || !tokens?.access) {
    console.warn('No valid authentication token available');
    return {};
  }
  
  return {
    'Authorization': `Bearer ${tokens.access}`,
    'Content-Type': 'application/json',
  };
};

/**
 * Get current access token from Redux store
 * Replaces direct localStorage access
 */
export const getAccessToken = () => {
  const state = store.getState();
  const tokens = selectAuthTokens(state);
  return tokens?.access || null;
};

/**
 * Get current user from Redux store
 * Centralized user access
 */
export const getCurrentUser = () => {
  const state = store.getState();
  return selectCurrentUser(state);
};

/**
 * Check if user is authenticated
 * Centralized authentication check
 */
export const isUserAuthenticated = () => {
  const state = store.getState();
  return selectIsAuthenticated(state);
};

/**
 * Create authenticated fetch wrapper
 * Automatically includes auth headers and handles common auth errors
 */
export const authenticatedFetch = async (url, options = {}) => {
  const authHeaders = getAuthHeaders();
  
  if (!authHeaders.Authorization) {
    throw new Error('Authentication required');
  }
  
  const fetchOptions = {
    ...options,
    headers: {
      ...authHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, fetchOptions);
    
    // Handle authentication errors consistently
    if (response.status === 401) {
      console.error('Authentication failed - token may be expired');
      // The apiSlice will handle token refresh automatically
      throw new Error('Authentication failed');
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('Authenticated fetch failed:', error);
    throw error;
  }
};

/**
 * Utility function to make authenticated API calls with JSON response
 * Handles common patterns used throughout the app
 */
export const authenticatedApiCall = async (url, options = {}) => {
  const response = await authenticatedFetch(url, options);
  
  // Return response for blob/file downloads
  if (options.responseType === 'blob') {
    return response;
  }
  
  // Parse JSON for regular API responses
  try {
    const data = await response.json();
    return { data, response };
  } catch (error) {
    // Handle responses with no body
    return { data: null, response };
  }
};

export default {
  getAuthHeaders,
  getAccessToken,
  getCurrentUser,
  isUserAuthenticated,
  authenticatedFetch,
  authenticatedApiCall,
};