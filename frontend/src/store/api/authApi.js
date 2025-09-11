import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { setCredentials, logout, setAccessToken, updateUser } from '../slices/authSlice';
import { getCSRFToken } from '../../lib/cookieUtils';
import { normalizeApiError } from '../../utils/apiErrors';

// Base query with automatic token handling and CSRF protection
const baseQuery = fetchBaseQuery({
  baseUrl: 'http://localhost:8000/api/auth/',
  credentials: 'include', // Include cookies for refresh token and session
  prepareHeaders: (headers, { getState }) => {
    // Get access token from Redux state (still stored in memory for security)
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

// Enhanced base query with automatic token refresh using cookies and queue management
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  // If we get a 401, handle token refresh with proper queuing
  if (result?.error?.status === 401) {
    const originalRequest = { args, api, extraOptions };

    if (isRefreshing) {
      // If refresh is already in progress, queue this request
      console.log('Token refresh in progress, queuing request...');
      try {
        const token = await new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        });
        
        if (token) {
          // Retry the original request with new token
          result = await baseQuery(args, api, extraOptions);
        }
        return result;
      } catch (err) {
        return result; // Return the original 401 error
      }
    }

    console.log('Token expired, attempting refresh using cookies...');
    isRefreshing = true;

    try {
      // Try to get new token using cookie-based refresh endpoint
      const refreshResult = await baseQuery(
        {
          url: 'refresh/',
          method: 'POST',
          // No body needed - refresh token comes from httpOnly cookie
        },
        api,
        extraOptions
      );

      if (refreshResult?.data?.access) {
        // Store the new access token in Redux
        const { access } = refreshResult.data;
        api.dispatch(setAccessToken(access));
        
        console.log('Token refreshed successfully');
        
        // Process queued requests
        processQueue(null, access);
        
        // Retry the original query with new token
        result = await baseQuery(args, api, extraOptions);
      } else {
        // Refresh failed, logout user
        console.log('Token refresh failed, logging out user...');
        processQueue(new Error('Token refresh failed'), null);
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

  return result;
};

// Define the auth API
export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'MFA'],
  endpoints: (builder) => ({
    // Authentication endpoints
    login: builder.mutation({
      query: (credentials) => ({
        url: 'login/',
        method: 'POST',
        body: credentials,
      }),
      transformErrorResponse: (response) => normalizeApiError(response),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data.access && data.refresh) {
            // Store tokens and user data
            dispatch(setCredentials({
              user: data.user,
              tokens: {
                access: data.access,
                refresh: data.refresh
              }
            }));
          }
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('Login error:', e);
        }
      },
      invalidatesTags: ['User'],
    }),

    register: builder.mutation({
      query: (userData) => ({
        url: 'register/',
        method: 'POST',
        body: userData,
      }),
      transformErrorResponse: (response) => normalizeApiError(response),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data.access && data.refresh) {
            // Store tokens and user data after successful registration
            dispatch(setCredentials({
              user: data.user,
              tokens: {
                access: data.access,
                refresh: data.refresh
              }
            }));
          }
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('Registration error:', e);
        }
      },
      invalidatesTags: ['User'],
    }),

    logout: builder.mutation({
      query: () => ({
        url: 'logout/',
        method: 'POST',
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('Logout error:', e);
        } finally {
          // Always clear credentials on logout attempt
          dispatch(logout());
        }
      },
      invalidatesTags: ['User', 'MFA'],
    }),

    // Password management endpoints
    requestPasswordReset: builder.mutation({
      query: (email) => ({
        url: 'password/reset/',
        method: 'POST',
        body: { email },
      }),
    }),

    confirmPasswordReset: builder.mutation({
      query: (resetData) => ({
        url: 'password/reset/confirm/',
        method: 'POST',
        body: resetData,
      }),
    }),

    changePassword: builder.mutation({
      query: (passwordData) => ({
        url: 'password/change/',
        method: 'POST',
        body: passwordData,
      }),
      async onQueryStarted(passwordData, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          // Update last password change timestamp if available from response
          // Backend doesn't return user data, so we just ensure cache consistency
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('Password change error:', e);
        }
      },
      invalidatesTags: ['User'],
    }),

    // MFA endpoints
    verifyMFA: builder.mutation({
      query: ({ code, mfa_token }) => ({
        url: 'mfa/verify/',
        method: 'POST',
        body: { code, mfa_token },
      }),
      transformErrorResponse: (response) => normalizeApiError(response),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data.access && data.refresh) {
            // Store tokens and user data after successful MFA verification
            dispatch(setCredentials({
              user: data.user,
              tokens: {
                access: data.access,
                refresh: data.refresh
              }
            }));
          }
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('MFA verification error:', e);
        }
      },
      invalidatesTags: ['User', 'MFA'],
    }),

    enrollMFA: builder.mutation({
      query: () => ({
        url: 'mfa/enroll/',
        method: 'POST',
      }),
      invalidatesTags: ['User', 'MFA'],
    }),

    confirmMFAEnrollment: builder.mutation({
      query: ({ device_id, code }) => ({
        url: 'mfa/enroll/',
        method: 'PUT',
        body: { device_id, code },
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          // Update user's MFA status in Redux immediately
          dispatch(updateUser({ is_mfa_enabled: true, mfa_enrolled: true }));
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('MFA enrollment error:', e);
        }
      },
      invalidatesTags: ['User', 'MFA'],
    }),

    disableMFA: builder.mutation({
      query: (data) => ({
        url: 'mfa/disable/',
        method: 'POST',
        body: data,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          // Update user's MFA status in Redux immediately
          dispatch(updateUser({ is_mfa_enabled: false, mfa_enrolled: false }));
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('MFA disable error:', e);
        }
      },
      invalidatesTags: ['User', 'MFA'],
    }),

    getMFAStatus: builder.query({
      query: () => 'mfa/status/',
      providesTags: ['MFA'],
    }),

    getMFABackupCodes: builder.query({
      query: () => 'mfa/backup-codes/',
      providesTags: ['MFA'],
    }),

    regenerateMFABackupCodes: builder.mutation({
      query: () => ({
        url: 'mfa/backup-codes/',
        method: 'POST',
      }),
      invalidatesTags: ['MFA'],
    }),

    // User profile endpoints
    getProfile: builder.query({
      query: () => 'me/',
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          // Always sync fresh API data with Redux on every profile fetch
          dispatch(updateUser(data));
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('Profile fetch error:', e);
        }
      },
      providesTags: ['User'],
    }),

    updateProfile: builder.mutation({
      query: (userData) => ({
        url: 'me/',
        method: 'PATCH',
        body: userData,
      }),
      async onQueryStarted(userData, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          // Update Redux store with fresh user data
          dispatch(updateUser(data));
        } catch (error) {
          const e = normalizeApiError(error?.error || error);
          console.error('Profile update error:', e);
        }
      },
      invalidatesTags: ['User'],
    }),

    // Token refresh (handled automatically by baseQueryWithReauth)
    refreshToken: builder.mutation({
      query: () => ({
        url: 'refresh/',
        method: 'POST',
      }),
    }),

    // CSRF token endpoint
    getCSRFToken: builder.query({
      query: () => ({
        url: 'csrf-token/',
        method: 'GET',
      }),
      // Don't cache CSRF tokens
      keepUnusedDataFor: 0,
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useRequestPasswordResetMutation,
  useConfirmPasswordResetMutation,
  useChangePasswordMutation,
  useVerifyMFAMutation,
  useEnrollMFAMutation,
  useConfirmMFAEnrollmentMutation,
  useDisableMFAMutation,
  useGetMFAStatusQuery,
  useGetMFABackupCodesQuery,
  useRegenerateMFABackupCodesMutation,
  useGetProfileQuery,
  useUpdateProfileMutation,
  useRefreshTokenMutation,
  useGetCSRFTokenQuery,
} = authApi;

export default authApi;
