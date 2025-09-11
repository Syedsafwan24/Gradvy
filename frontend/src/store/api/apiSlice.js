import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { setCredentials, logout } from '../slices/authSlice';
import { getCSRFToken } from '../../lib/cookieUtils';
import { normalizeApiError } from '../../utils/apiErrors';

// Base query with automatic token handling and CSRF protection
const baseQuery = fetchBaseQuery({
  baseUrl: 'http://localhost:8000/api/',
  credentials: 'include', // Include cookies for refresh token and session
  prepareHeaders: (headers, { getState }) => {
    // Get access token from Redux state
    const token = getState().auth.tokens?.access;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    
    // Add CSRF token for state-changing requests
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken);
    }
    
    headers.set('Content-Type', 'application/json');
    return headers;
  },
});

// Token refresh queue to prevent race conditions
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

// Enhanced base query with automatic token refresh
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  // If we get a 401, handle token refresh
  if (result?.error?.status === 401) {
    if (isRefreshing) {
      // If already refreshing, queue this request
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        // Retry the original request with new token
        return baseQuery(args, api, extraOptions);
      }).catch((error) => {
        throw error;
      });
    }

    isRefreshing = true;

    try {
      // Try to refresh tokens using HTTP-only cookies
      const refreshResult = await baseQuery(
        {
          url: 'auth/refresh/',
          method: 'POST',
        },
        api,
        extraOptions
      );

      if (refreshResult?.data?.access) {
        // Update Redux with new token
        api.dispatch(setCredentials({
          user: api.getState().auth.user,
          tokens: {
            access: refreshResult.data.access,
            refresh: null // Keep refresh token in HTTP-only cookie
          }
        }));

        processQueue(null, refreshResult.data.access);
        
        // Retry the original request
        result = await baseQuery(args, api, extraOptions);
      } else {
        processQueue(new Error('Refresh failed'), null);
        api.dispatch(logout());
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      processQueue(error, null);
      api.dispatch(logout());
    } finally {
      isRefreshing = false;
    }
  }

  // Attach normalized error for consistent handling downstream
  if (result?.error) {
    try {
      result.error.normalized = normalizeApiError(result.error);
    } catch {}
  }
  return result;
};

// Define the main API slice
export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'MFA', 'UserPreferences', 'Analytics', 'Recommendations'],
  endpoints: (builder) => ({}), // Endpoints will be injected by other API files
});

export default apiSlice;
