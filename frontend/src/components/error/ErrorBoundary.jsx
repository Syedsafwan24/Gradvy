// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/error/ErrorBoundary.jsx
// Centralized error boundary component for catching and handling React errors
// Provides graceful error handling with user-friendly fallback UI and error reporting
// RELEVANT FILES: app/layout.jsx, app/app/layout.jsx, any page components, ErrorFallback.jsx

'use client';

import React from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: Date.now().toString(36) + Math.random().toString(36).substr(2)
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Report error to monitoring service (e.g., Sentry, LogRocket)
    this.reportError(error, errorInfo);
  }

  reportError = (error, errorInfo) => {
    // In production, this would send to error monitoring service
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error, { extra: errorInfo });
      console.error('Production error reported:', { error, errorInfo });
    }

    // Could also send to custom API endpoint
    try {
      fetch('/api/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: error.message,
          stack: error.stack,
          errorInfo: errorInfo.componentStack,
          timestamp: new Date().toISOString(),
          errorId: this.state.errorId,
          userAgent: navigator.userAgent,
          url: window.location.href
        })
      }).catch(() => {}); // Fail silently to avoid infinite loops
    } catch (e) {
      // Fail silently
    }
  };

  handleReset = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null 
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleHome = () => {
    window.location.href = '/app';
  };

  copyErrorDetails = () => {
    const errorDetails = {
      errorId: this.state.errorId,
      message: this.state.error?.message,
      stack: this.state.error?.stack,
      componentStack: this.state.errorInfo?.componentStack,
      timestamp: new Date().toISOString()
    };

    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      .then(() => {
        // Could show toast notification here
        alert('Error details copied to clipboard');
      })
      .catch(() => {
        console.error('Failed to copy error details');
      });
  };

  render() {
    if (this.state.hasError) {
      // Render custom fallback UI
      const { fallback: CustomFallback, level = 'page' } = this.props;

      if (CustomFallback) {
        return (
          <CustomFallback
            error={this.state.error}
            errorInfo={this.state.errorInfo}
            resetError={this.handleReset}
            errorId={this.state.errorId}
          />
        );
      }

      // Default error UI based on error level
      if (level === 'component') {
        return (
          <Card className="p-6 m-4 border-red-200 bg-red-50">
            <div className="flex items-center space-x-2 text-red-700 mb-3">
              <AlertTriangle className="h-5 w-5" />
              <h3 className="font-semibold">Component Error</h3>
            </div>
            <p className="text-red-600 text-sm mb-3">
              This component encountered an error and couldn't render properly.
            </p>
            <Button 
              onClick={this.handleReset} 
              variant="outline" 
              size="sm"
              className="text-red-700 border-red-300 hover:bg-red-100"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </Card>
        );
      }

      // Full page error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg p-8 text-center">
            <div className="mb-6">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Something went wrong
              </h1>
              <p className="text-gray-600 mb-4">
                We're sorry, but something unexpected happened. Our team has been notified.
              </p>
              
              {this.state.errorId && (
                <div className="bg-gray-100 rounded-lg p-3 mb-6">
                  <p className="text-sm text-gray-600">
                    Error ID: <span className="font-mono text-gray-800">{this.state.errorId}</span>
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  onClick={this.handleReset} 
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
                <Button 
                  onClick={this.handleReload} 
                  variant="outline"
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reload Page
                </Button>
              </div>
              
              <Button 
                onClick={this.handleHome} 
                variant="outline"
                className="w-full"
              >
                <Home className="h-4 w-4 mr-2" />
                Go to Homepage
              </Button>
            </div>

            {/* Debug info for development */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 flex items-center">
                  <Bug className="h-4 w-4 mr-2" />
                  Show Error Details (Development)
                </summary>
                <div className="mt-3 p-3 bg-gray-900 text-green-400 rounded-lg text-xs overflow-auto max-h-40">
                  <div className="mb-2">
                    <strong>Error:</strong> {this.state.error.message}
                  </div>
                  <div className="mb-2">
                    <strong>Stack:</strong>
                    <pre className="whitespace-pre-wrap mt-1">{this.state.error.stack}</pre>
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>Component Stack:</strong>
                      <pre className="whitespace-pre-wrap mt-1">{this.state.errorInfo.componentStack}</pre>
                    </div>
                  )}
                </div>
                <Button 
                  onClick={this.copyErrorDetails} 
                  variant="ghost" 
                  size="sm"
                  className="mt-2 text-xs"
                >
                  Copy Error Details
                </Button>
              </details>
            )}
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;