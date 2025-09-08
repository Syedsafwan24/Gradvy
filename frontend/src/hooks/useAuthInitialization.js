/**
 * Authentication Initialization Hook
 * Handles app startup authentication setup including CSRF tokens
 */

import { useEffect, useState } from 'react';
import { useGetCSRFTokenQuery } from '../store/api/authApi';
import { initializeCookieManagement } from '../lib/cookieUtils';

const useAuthInitialization = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState(null);

  // Get CSRF token on app startup
  const {
    data: csrfData,
    error: csrfError,
    isLoading: csrfLoading
  } = useGetCSRFTokenQuery(undefined, {
    // Only fetch once on startup
    refetchOnMount: true,
    refetchOnReconnect: false,
    refetchOnFocus: false,
  });

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Initialize cookie management
        initializeCookieManagement();
        
        // Wait for CSRF token to be loaded
        if (!csrfLoading && !csrfError) {
          console.log('Authentication system initialized successfully');
          setIsInitialized(true);
          setInitError(null);
        } else if (csrfError) {
          console.warn('CSRF token fetch failed, continuing without it:', csrfError);
          // Continue initialization even if CSRF fails
          setIsInitialized(true);
          setInitError(csrfError);
        }
      } catch (error) {
        console.error('Failed to initialize authentication system:', error);
        setInitError(error);
        setIsInitialized(true); // Continue app loading even if init fails
      }
    };

    initializeAuth();
  }, [csrfLoading, csrfError]);

  return {
    isInitialized,
    initError,
    csrfToken: csrfData?.csrf_token,
    csrfLoading
  };
};

export default useAuthInitialization;