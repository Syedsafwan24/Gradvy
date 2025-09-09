'use client';

import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useRouter, usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Loader2, AlertCircle } from 'lucide-react';
import { 
  selectIsAuthenticated, 
  selectAuthLoading, 
  selectCurrentUser,
  selectAccessToken 
} from '@/store/slices/authSlice';

/**
 * Protected Route Component
 * Handles authentication checks, loading states, and redirects
 */
const ProtectedRoute = ({ 
  children, 
  requireAuth = true, 
  redirectTo = '/login',
  loadingComponent = null,
  fallbackComponent = null,
  checkPermissions = null,
  className = ''
}) => {
  const router = useRouter();
  const pathname = usePathname();
  const dispatch = useDispatch();
  
  // Redux state
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const authLoading = useSelector(selectAuthLoading);
  const user = useSelector(selectCurrentUser);
  const accessToken = useSelector(selectAccessToken);
  
  // Local state for component loading
  const [isChecking, setIsChecking] = useState(true);
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);
  const [error, setError] = useState(null);

  // Simplified authentication check without profile query to prevent race conditions
  const [isInitialized, setIsInitialized] = useState(false);

  // Simplified authentication check
  useEffect(() => {
    const checkAuth = async () => {
      // Wait a moment for Redux state to initialize
      if (!isInitialized) {
        setTimeout(() => setIsInitialized(true), 100);
        return;
      }

      setIsChecking(true);
      setError(null);

      try {
        if (requireAuth) {
          // Simple check: both isAuthenticated and accessToken must be present
          const hasValidAuth = isAuthenticated && accessToken;
          
          console.log('🔒 ProtectedRoute: Auth check:', { 
            isAuthenticated, 
            hasAccessToken: !!accessToken, 
            hasValidAuth,
            pathname 
          });
          
          if (!hasValidAuth) {
            console.log('🔒 ProtectedRoute: Missing authentication, redirecting to login');
            
            // Store the current path for redirect after login
            if (typeof window !== 'undefined') {
              sessionStorage.setItem('redirectPath', pathname);
            }
            
            router.push(`${redirectTo}?next=${encodeURIComponent(pathname)}`);
            return;
          }

          // Check custom permissions if provided
          if (checkPermissions && user) {
            const hasPermission = await checkPermissions(user);
            if (!hasPermission) {
              console.log('🔒 ProtectedRoute: Insufficient permissions');
              setError('You do not have permission to access this page.');
              return;
            }
          }
        } else {
          // For non-protected routes (like login page)
          if (isAuthenticated && accessToken) {
            console.log('🔓 ProtectedRoute: User already authenticated, redirecting to dashboard');
            const savedPath = typeof window !== 'undefined' ? sessionStorage.getItem('redirectPath') : null;
            const redirectPath = savedPath || '/dashboard';
            if (typeof window !== 'undefined') {
              sessionStorage.removeItem('redirectPath');
            }
            router.push(redirectPath);
            return;
          }
        }

        setHasCheckedAuth(true);
      } catch (error) {
        console.error('🔒 ProtectedRoute: Auth check error:', error);
        setError('Authentication check failed. Please try again.');
      } finally {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [isInitialized, isAuthenticated, accessToken, requireAuth, pathname]);

  // Show loading state
  if (isChecking || authLoading || !isInitialized) {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key="loading"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={`min-h-screen flex items-center justify-center ${className}`}
        >
          {loadingComponent || <DefaultLoadingComponent />}
        </motion.div>
      </AnimatePresence>
    );
  }

  // Show error state
  if (error) {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key="error"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className={`min-h-screen flex items-center justify-center ${className}`}
        >
          {fallbackComponent || <DefaultErrorComponent error={error} />}
        </motion.div>
      </AnimatePresence>
    );
  }

  // Show children if authentication check passed
  if (hasCheckedAuth) {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key="content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={className}
        >
          {children}
        </motion.div>
      </AnimatePresence>
    );
  }

  // Default return while checking
  return (
    <div className={`min-h-screen flex items-center justify-center ${className}`}>
      <DefaultLoadingComponent />
    </div>
  );
};

/**
 * Default Loading Component
 */
const DefaultLoadingComponent = () => (
  <div className="flex flex-col items-center justify-center space-y-4">
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full"
    />
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="flex items-center space-x-2 text-gray-600"
    >
      <Shield className="w-4 h-4" />
      <span>Verifying authentication...</span>
    </motion.div>
  </div>
);

/**
 * Default Error Component
 */
const DefaultErrorComponent = ({ error }) => (
  <div className="max-w-md mx-auto text-center">
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: "spring", duration: 0.5 }}
      className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"
    >
      <AlertCircle className="w-8 h-8 text-red-600" />
    </motion.div>
    <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
    <p className="text-gray-600 mb-4">{error}</p>
    <button
      onClick={() => window.location.reload()}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
    >
      Try Again
    </button>
  </div>
);

/**
 * Higher-Order Component for easy route protection
 */
export const withAuth = (WrappedComponent, options = {}) => {
  return function AuthenticatedComponent(props) {
    return (
      <ProtectedRoute {...options}>
        <WrappedComponent {...props} />
      </ProtectedRoute>
    );
  };
};

/**
 * Hook for checking authentication in components
 */
export const useAuthGuard = (options = {}) => {
  const { requireAuth = true, redirectTo = '/login' } = options;
  const router = useRouter();
  const pathname = usePathname();
  
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const accessToken = useSelector(selectAccessToken);
  const user = useSelector(selectCurrentUser);

  const checkAuth = () => {
    if (requireAuth && (!isAuthenticated || !accessToken)) {
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('redirectPath', pathname);
      }
      router.push(`${redirectTo}?next=${encodeURIComponent(pathname)}`);
      return false;
    }
    return true;
  };

  return {
    isAuthenticated,
    user,
    accessToken,
    checkAuth,
  };
};

export default ProtectedRoute;
