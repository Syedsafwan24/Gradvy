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
    
    // Try to refresh the token
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
      api.dispatch(logout());
    }
  }

  return result;
};

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User'],
  endpoints: (builder) => ({
    // User Registration
    register: builder.mutation({
      query: (userData) => ({
        url: 'register/',
        method: 'POST',
        body: userData,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          // Transform backend response to match frontend expectations
          dispatch(setCredentials({
            user: data.user,
            access: data.access,
            refresh: data.refresh
          }));
        } catch (error) {
          console.error('Registration failed:', error);
        }
      },
    }),

    // User Login
    login: builder.mutation({
      query: (credentials) => ({
        url: 'login/',
        method: 'POST',
        body: credentials,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data.mfa_required) {
            // MFA required, don't set credentials yet
            return data;
          } else {
            // Regular login successful - transform response
            dispatch(setCredentials({
              user: data.user,
              access: data.access,
              refresh: data.refresh
            }));
          }
        } catch (error) {
          console.error('Login failed:', error);
        }
      },
    }),

    // MFA Verification
    verifyMFA: builder.mutation({
      query: ({ code, mfa_token }) => ({
        url: 'mfa/verify/',
        method: 'POST',
        body: { code, mfa_token },
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          // Transform backend response for MFA verification
          dispatch(setCredentials({
            user: data.user,
            access: data.access,
            refresh: data.refresh
          }));
        } catch (error) {
          console.error('MFA verification failed:', error);
        }
      },
    }),

    // User Logout
    logout: builder.mutation({
      query: () => ({
        url: 'logout/',
        method: 'POST',
        body: { refresh: '' }, // We'll handle the refresh token in onQueryStarted
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled, getState }) {
        // Get refresh token from state
        const state = getState();
        const refreshToken = state.auth.tokens?.refresh;
        
        try {
          // If we have a refresh token, make the actual logout request
          if (refreshToken) {
            await fetch('http://localhost:8000/api/auth/logout/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.auth.tokens?.access || ''}`,
              },
              credentials: 'include',
              body: JSON.stringify({ refresh: refreshToken }),
            });
          }
        } catch (error) {
          console.log('Logout API failed, but clearing local state anyway:', error);
        }
        
        // Always clear local state regardless of backend response
        dispatch(logout());
      },
      transformResponse: (response, meta, arg) => {
        // Backend returns empty response with 200 status, transform to success
        return { success: true };
      },
      transformErrorResponse: (response, meta, arg) => {
        // Even on error, we want to consider logout as successful locally
        return { success: true };
      },
    }),

    // Get Current User Profile
    getProfile: builder.query({
      query: () => 'me/',
      providesTags: ['User'],
      transformResponse: (response) => response.user || response,
    }),

    // Password Reset Request
    requestPasswordReset: builder.mutation({
      query: (email) => ({
        url: 'password/reset/',
        method: 'POST',
        body: { email },
      }),
    }),

    // Change Password
    changePassword: builder.mutation({
      query: (passwordData) => ({
        url: 'password/change/',
        method: 'POST',
        body: passwordData,
      }),
    }),

    // Refresh Token
    refreshToken: builder.mutation({
      query: () => ({
        url: 'refresh/',
        method: 'POST',
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data.access) {
            dispatch(setAccessToken(data.access));
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          dispatch(logout());
        }
      },
    }),
  }),
});

export const {
  useRegisterMutation,
  useLoginMutation,
  useVerifyMFAMutation,
  useLogoutMutation,
  useGetProfileQuery,
  useRequestPasswordResetMutation,
  useChangePasswordMutation,
  useRefreshTokenMutation,
} = authApi;
