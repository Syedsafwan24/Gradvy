// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/error/ErrorFallback.jsx
// Reusable error fallback UI components for different error scenarios
// Provides flexible error display options for various contexts
// RELEVANT FILES: ErrorBoundary.jsx, app/layout.jsx, individual page components

'use client';

import React from 'react';
import { AlertTriangle, RefreshCw, Home, FileX, Wifi, Server } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// Generic error fallback component
export const GenericErrorFallback = ({ error, resetError, errorId }) => (
  <Card className="p-8 text-center max-w-md mx-auto">
    <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
      <AlertTriangle className="h-8 w-8 text-red-600" />
    </div>
    <h2 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h2>
    <p className="text-gray-600 mb-6">
      An unexpected error occurred. Please try again or contact support if the problem persists.
    </p>
    {errorId && (
      <Badge variant="outline" className="mb-4 text-xs">
        Error ID: {errorId}
      </Badge>
    )}
    <div className="space-y-2">
      <Button onClick={resetError} className="w-full">
        <RefreshCw className="h-4 w-4 mr-2" />
        Try Again
      </Button>
      <Button variant="outline" onClick={() => window.location.reload()} className="w-full">
        Reload Page
      </Button>
    </div>
  </Card>
);

// Component-level error fallback (smaller, inline)
export const ComponentErrorFallback = ({ error, resetError, componentName }) => (
  <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
    <div className="flex items-center space-x-2 text-red-700 mb-2">
      <AlertTriangle className="h-4 w-4" />
      <span className="text-sm font-medium">
        {componentName ? `${componentName} Error` : 'Component Error'}
      </span>
    </div>
    <p className="text-red-600 text-sm mb-3">
      This component couldn't load properly.
    </p>
    <Button 
      onClick={resetError} 
      variant="outline" 
      size="sm"
      className="text-red-700 border-red-300 hover:bg-red-100"
    >
      <RefreshCw className="h-3 w-3 mr-2" />
      Retry
    </Button>
  </div>
);

// Network/API error fallback
export const NetworkErrorFallback = ({ resetError, onRetry }) => (
  <Card className="p-6 text-center max-w-sm mx-auto">
    <div className="mx-auto w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-4">
      <Wifi className="h-6 w-6 text-orange-600" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">Connection Issue</h3>
    <p className="text-gray-600 mb-4 text-sm">
      Unable to connect to our servers. Please check your internet connection.
    </p>
    <div className="space-y-2">
      <Button onClick={onRetry || resetError} size="sm" className="w-full">
        <RefreshCw className="h-4 w-4 mr-2" />
        Try Again
      </Button>
    </div>
  </Card>
);

// Server error fallback
export const ServerErrorFallback = ({ resetError, errorId }) => (
  <Card className="p-6 text-center max-w-sm mx-auto">
    <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
      <Server className="h-6 w-6 text-red-600" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">Server Error</h3>
    <p className="text-gray-600 mb-4 text-sm">
      Our servers are experiencing issues. We're working to fix this.
    </p>
    {errorId && (
      <Badge variant="outline" className="mb-4 text-xs">
        Error ID: {errorId}
      </Badge>
    )}
    <div className="space-y-2">
      <Button onClick={resetError} size="sm" className="w-full">
        <RefreshCw className="h-4 w-4 mr-2" />
        Try Again
      </Button>
      <Button variant="outline" onClick={() => window.location.href = '/app'} size="sm" className="w-full">
        <Home className="h-4 w-4 mr-2" />
        Go Home
      </Button>
    </div>
  </Card>
);

// Page not found fallback
export const NotFoundErrorFallback = ({ resetError }) => (
  <Card className="p-8 text-center max-w-md mx-auto">
    <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
      <FileX className="h-8 w-8 text-gray-600" />
    </div>
    <h2 className="text-xl font-semibold text-gray-900 mb-2">Page Not Found</h2>
    <p className="text-gray-600 mb-6">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <div className="space-y-2">
      <Button onClick={() => window.location.href = '/app'} className="w-full">
        <Home className="h-4 w-4 mr-2" />
        Go to Homepage
      </Button>
      <Button variant="outline" onClick={() => window.history.back()} className="w-full">
        Go Back
      </Button>
    </div>
  </Card>
);

// Minimal inline error display
export const InlineErrorFallback = ({ error, resetError, message }) => (
  <div className="flex items-center justify-center p-4 text-red-600 bg-red-50 border border-red-200 rounded">
    <AlertTriangle className="h-4 w-4 mr-2" />
    <span className="text-sm mr-3">{message || 'Failed to load'}</span>
    <Button variant="ghost" size="sm" onClick={resetError} className="text-red-600 hover:text-red-700">
      <RefreshCw className="h-3 w-3" />
    </Button>
  </div>
);

// Error boundary wrapper with different fallback types
export const ErrorBoundaryWrapper = ({ children, fallbackType = 'generic', componentName, ...props }) => {
  const getFallbackComponent = () => {
    switch (fallbackType) {
      case 'component':
        return (errorProps) => <ComponentErrorFallback {...errorProps} componentName={componentName} />;
      case 'network':
        return NetworkErrorFallback;
      case 'server':
        return ServerErrorFallback;
      case 'notfound':
        return NotFoundErrorFallback;
      case 'inline':
        return InlineErrorFallback;
      default:
        return GenericErrorFallback;
    }
  };

  return (
    <ErrorBoundary fallback={getFallbackComponent()} level={fallbackType} {...props}>
      {children}
    </ErrorBoundary>
  );
};