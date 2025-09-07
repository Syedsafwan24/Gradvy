import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { setCredentials, logout, setAccessToken } from '../slices/authSlice';

// Base query with automatic token handling
const baseQuery = fetchBaseQuery({
  baseUrl: 'http://localhost:8000/api/auth/',
  credentials: 'include', // Include cookies for refresh token
  prepareHeaders: (headers, { getState }) => {
    // Get token from Redux state
    const token = getState().auth.tokens?.access;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    headers.set('Content-Type', 'application/json');
    return headers;
  },
});

// Enhanced base query with automatic token refresh
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  // If we get a 401, try to refresh the token
  if (result?.error?.status === 401) {
    console.log('Token expired, attempting refresh...');
    
    // Try to get new token using refresh endpoint
    const refreshResult = await baseQuery(
      {
        url: 'refresh/',
        method: 'POST',
      },
      api,
      extraOptions
    );

    if (refreshResult?.data) {
      // Store the new token
      const { access } = refreshResult.data;
      api.dispatch(setAccessToken(access));
      
      // Retry the original query with new token
      result = await baseQuery(args, api, extraOptions);
    } else {
      // Refresh failed, logout user
      console.log('Token refresh failed, logging out...');
      api.dispatch(logout());
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
          console.error('Login failed:', error);
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
          console.error('Registration failed:', error);
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
          console.error('Logout error:', error);
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
    }),

    // MFA endpoints
    verifyMFA: builder.mutation({
      query: ({ code, mfa_token }) => ({
        url: 'mfa/verify/',
        method: 'POST',
        body: { code, mfa_token },
      }),
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
          console.error('MFA verification failed:', error);
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
      invalidatesTags: ['User', 'MFA'],
    }),

    disableMFA: builder.mutation({
      query: (data) => ({
        url: 'mfa/disable/',
        method: 'POST',
        body: data,
      }),
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
      providesTags: ['User'],
    }),

    updateProfile: builder.mutation({
      query: (userData) => ({
        url: 'me/',
        method: 'PATCH',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),

    // Token refresh (handled automatically by baseQueryWithReauth)
    refreshToken: builder.mutation({
      query: () => ({
        url: 'refresh/',
        method: 'POST',
      }),
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
} = authApi;

export default authApi;
