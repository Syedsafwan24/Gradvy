'use client';

import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { initializeAuth, setCredentials } from '@/store/slices/authSlice';
import { selectCurrentUser } from '@/store/slices/authSlice';

/**
 * AuthInitializer Component
 * Runs on app startup to ensure clean authentication state
 * This prevents infinite redirect loops caused by inconsistent state
 */
const AuthInitializer = ({ children }) => {
  const dispatch = useDispatch();
  const user = useSelector(selectCurrentUser);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initializeAuthentication = async () => {
      console.log('🔄 AuthInitializer: Starting authentication initialization');
      
      // Add a small delay to ensure Redux persistence is fully loaded
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Get the current user from Redux after persistence is loaded
      const currentUser = user;
      
      // Reset authentication state first
      dispatch(initializeAuth());

      try {
        // If we have a persisted user, try to restore authentication
        if (currentUser) {
          console.log('👤 AuthInitializer: User found in persistence, attempting token refresh');
          
          // Try to refresh tokens using HTTP-only cookies
          const response = await fetch('http://localhost:8000/api/auth/refresh/', {
            method: 'POST',
            credentials: 'include', // Important for HTTP-only cookies
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const data = await response.json();
            
            if (data.access) {
              console.log('✅ AuthInitializer: Token refresh successful');
              // Restore authentication state
              dispatch(setCredentials({
                user: currentUser,
                tokens: {
                  access: data.access,
                  refresh: null, // Refresh token is in HTTP-only cookie
                }
              }));
            } else {
              console.log('❌ AuthInitializer: No access token in refresh response');
            }
          } else {
            console.log('❌ AuthInitializer: Token refresh failed, user needs to login');
          }
        } else {
          console.log('👤 AuthInitializer: No user found in persistence');
        }
      } catch (error) {
        console.error('❌ AuthInitializer: Error during authentication initialization:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeAuthentication();
  }, [dispatch]);

  // Show loading state while initializing
  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Initializing...</p>
        </div>
      </div>
    );
  }

  return children;
};

export default AuthInitializer;