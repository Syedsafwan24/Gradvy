'use client';

import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setCredentials, logout, setLoading, setError } from '@/store/slices/authSlice';
import { 
  selectCurrentUser, 
  selectAreTokensValid, 
  selectShouldRefreshTokens,
  selectIsAuthenticated,
  selectAuthLoading
} from '@/store/slices/authSlice';
import { API_CONFIG } from '@/config/api';

/**
 * AuthInitializer Component
 * Handles authentication state restoration after Redux persist rehydration
 * Fixes race conditions and provides proper error handling
 */
const AuthInitializer = ({ children, persistedUser }) => {
  const dispatch = useDispatch();
  
  // Auth state selectors
  const user = useSelector(selectCurrentUser);
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const areTokensValid = useSelector(selectAreTokensValid);
  const shouldRefreshTokens = useSelector(selectShouldRefreshTokens);
  const authLoading = useSelector(selectAuthLoading);
  
  // Local state
  const [isInitialized, setIsInitialized] = useState(false);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const initializeAuthentication = async () => {
      try {
        // If we already have valid tokens, we're good to go
        if (areTokensValid && isAuthenticated) {
          console.log('✅ AuthInitializer: Valid tokens found, authentication restored');
          setIsInitialized(true);
          return;
        }

        // If we have user data but invalid/missing tokens, try to refresh
        if (user && shouldRefreshTokens) {
          console.log('🔄 AuthInitializer: Attempting token refresh for user:', user.email);
          dispatch(setLoading(true));

          try {
            const response = await fetch(`${API_CONFIG.AUTH_BASE_URL}${API_CONFIG.ENDPOINTS.REFRESH}`, {
              method: 'POST',
              credentials: 'include', // Include HTTP-only refresh token cookie
              headers: {
                'Content-Type': 'application/json',
              },
            });

            if (!isMounted) return; // Component unmounted during fetch

            if (response.ok) {
              const data = await response.json();
              
              if (data.access) {
                console.log('✅ AuthInitializer: Token refresh successful');
                dispatch(setCredentials({
                  user: user,
                  tokens: {
                    access: data.access,
                    refresh: null, // Refresh token stays in HTTP-only cookie
                  }
                }));
                setAuthError(null);
              } else {
                console.warn('⚠️ AuthInitializer: Token refresh failed - no access token in response');
                dispatch(logout());
                setAuthError('Session expired. Please log in again.');
              }
            } else if (response.status === 401) {
              console.warn('⚠️ AuthInitializer: Refresh token invalid or expired');
              dispatch(logout());
              setAuthError(null); // Don't show error for expired refresh tokens
            } else {
              console.error('❌ AuthInitializer: Token refresh failed with status:', response.status);
              // Keep user data but mark as unauthenticated - they can try to log in
              dispatch(logout());
              setAuthError('Unable to restore session. Please log in again.');
            }
          } catch (fetchError) {
            if (!isMounted) return;
            
            console.error('❌ AuthInitializer: Token refresh network error:', fetchError);
            // On network error, keep user data but show offline state
            setAuthError('Network error. Please check your connection and try again.');
          }
        } else if (!user) {
          // No user data at all - clean slate
          console.log('ℹ️ AuthInitializer: No user data found, clean auth state');
          dispatch(logout()); // Ensure clean state
        } else {
          // User exists but no token refresh needed (edge case)
          console.log('ℹ️ AuthInitializer: User exists, no token refresh needed');
        }

      } catch (error) {
        if (!isMounted) return;
        
        console.error('❌ AuthInitializer: Critical error during initialization:', error);
        setAuthError('Authentication initialization failed. Please refresh the page.');
      } finally {
        if (isMounted) {
          dispatch(setLoading(false));
          setIsInitialized(true);
        }
      }
    };

    // Small delay to ensure component is mounted and Redux state is stable
    const timeoutId = setTimeout(initializeAuthentication, 50);

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, [user, areTokensValid, shouldRefreshTokens, isAuthenticated, dispatch]);

  // Show loading state while initializing
  if (!isInitialized || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-4">
          <div className="relative">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
          </div>
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900">Initializing Gradvy</p>
            <p className="text-sm text-gray-600">Restoring your session...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state if there's an authentication error
  if (authError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full mx-auto bg-white p-8 rounded-lg shadow-sm border border-red-200">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Authentication Error</h3>
              <p className="text-sm text-gray-600 mt-2">{authError}</p>
            </div>
            <div className="space-y-2">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Refresh Page
              </button>
              <button
                onClick={() => {
                  dispatch(logout());
                  setAuthError(null);
                  setIsInitialized(true);
                }}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Continue Without Session
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return children;
};

export default AuthInitializer;