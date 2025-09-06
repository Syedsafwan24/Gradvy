'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated, selectAuthLoading } from '../../store/slices/authSlice';
import { useGetProfileQuery } from '../../store/api/authApi';

const ProtectedRoute = ({ children, redirectTo = '/auth/login' }) => {
  const router = useRouter();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const authLoading = useSelector(selectAuthLoading);
  
  // Try to get user profile to validate token
  const { isLoading: isProfileLoading, error: profileError } = useGetProfileQuery(undefined, {
    skip: !isAuthenticated,
  });

  useEffect(() => {
    // If not authenticated and not loading, redirect to login
    if (!isAuthenticated && !authLoading && !isProfileLoading) {
      router.push(redirectTo);
    }
    
    // If profile fetch fails (invalid token), redirect to login
    if (profileError && profileError.status === 401) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, authLoading, isProfileLoading, profileError, router, redirectTo]);

  // Show loading state while checking authentication
  if (authLoading || isProfileLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show loading if not authenticated (will redirect)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Render children if authenticated
  return <>{children}</>;
};

export default ProtectedRoute;
