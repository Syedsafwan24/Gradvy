// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/hooks/useErrorHandler.js
// Custom hook for handling errors in functional components
// Provides error catching and reporting functionality with React Error Boundaries
// RELEVANT FILES: ErrorBoundary.jsx, ErrorFallback.jsx, any component using error handling

'use client';

import { useState, useCallback, useEffect } from 'react';

/**
 * Custom hook for error handling in functional components
 * Works with ErrorBoundary to provide comprehensive error management
 */
export const useErrorHandler = (defaultError = null) => {
  const [error, setError] = useState(defaultError);
  const [isLoading, setIsLoading] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  // Handle async operations with automatic error catching
  const handleAsync = useCallback(async (asyncFn, options = {}) => {
    const { 
      onSuccess, 
      onError, 
      maxRetries = 3, 
      retryDelay = 1000,
      loadingState = true 
    } = options;

    if (loadingState) setIsLoading(true);
    setError(null);

    try {
      const result = await asyncFn();
      setRetryCount(0);
      if (onSuccess) onSuccess(result);
      return result;
    } catch (err) {
      console.error('Async operation failed:', err);
      setError(err);
      
      // Auto-retry logic for network errors
      if (retryCount < maxRetries && isNetworkError(err)) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          handleAsync(asyncFn, options);
        }, retryDelay * Math.pow(2, retryCount)); // Exponential backoff
        return;
      }

      if (onError) onError(err);
      throw err; // Re-throw to be caught by ErrorBoundary
    } finally {
      if (loadingState) setIsLoading(false);
    }
  }, [retryCount]);

  // Manually set an error (useful for custom error scenarios)
  const setCustomError = useCallback((error, context = {}) => {
    const enhancedError = new Error(error.message || error);
    enhancedError.context = context;
    enhancedError.timestamp = new Date().toISOString();
    setError(enhancedError);
  }, []);

  // Clear the current error
  const clearError = useCallback(() => {
    setError(null);
    setRetryCount(0);
  }, []);

  // Retry the last failed operation
  const retry = useCallback(() => {
    clearError();
    // Trigger re-render to retry operation
    setRetryCount(prev => prev + 1);
  }, [clearError]);

  // Report error to monitoring service
  const reportError = useCallback((error, additionalInfo = {}) => {
    // Enhanced error reporting
    const errorReport = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      url: typeof window !== 'undefined' ? window.location.href : '',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      retryCount,
      ...additionalInfo
    };

    // Send to monitoring service (Sentry, LogRocket, etc.)
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error, { extra: errorReport });
      console.error('Error reported:', errorReport);
    }

    // Send to custom API endpoint
    try {
      fetch('/api/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorReport)
      }).catch(() => {}); // Fail silently
    } catch (e) {
      // Fail silently to avoid infinite loops
    }
  }, [retryCount]);

  // Auto-report errors when they occur
  useEffect(() => {
    if (error) {
      reportError(error);
    }
  }, [error, reportError]);

  return {
    error,
    isLoading,
    retryCount,
    handleAsync,
    setError: setCustomError,
    clearError,
    retry,
    reportError,
    hasError: !!error
  };
};

/**
 * Hook for handling API errors specifically
 */
export const useApiErrorHandler = () => {
  const { handleAsync, ...rest } = useErrorHandler();

  const handleApiCall = useCallback(async (apiCall, options = {}) => {
    return handleAsync(apiCall, {
      ...options,
      onError: (error) => {
        // Enhanced API error handling
        if (error.response) {
          // HTTP error responses
          console.error(`API Error ${error.response.status}:`, error.response.data);
        } else if (error.request) {
          // Network error
          console.error('Network Error:', error.message);
        } else {
          // Other errors
          console.error('API Call Error:', error.message);
        }
        
        if (options.onError) options.onError(error);
      }
    });
  }, [handleAsync]);

  return {
    ...rest,
    handleApiCall
  };
};

/**
 * Hook for component-level error boundaries
 */
export const useComponentError = (componentName) => {
  const [componentError, setComponentError] = useState(null);

  const handleComponentError = useCallback((error, errorInfo) => {
    console.error(`Error in ${componentName}:`, error, errorInfo);
    setComponentError({ error, errorInfo, componentName });
  }, [componentName]);

  const resetComponentError = useCallback(() => {
    setComponentError(null);
  }, []);

  return {
    componentError,
    handleComponentError,
    resetComponentError,
    hasComponentError: !!componentError
  };
};

// Utility functions
const isNetworkError = (error) => {
  return (
    error.code === 'NETWORK_ERROR' ||
    error.message.includes('fetch') ||
    error.message.includes('NetworkError') ||
    error.name === 'TypeError' && error.message.includes('Failed to fetch')
  );
};

export default useErrorHandler;