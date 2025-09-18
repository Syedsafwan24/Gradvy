// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/error/ApiErrorDisplay.jsx
// Enhanced API error display component for consistent error messaging
// Handles standardized API responses and provides user-friendly error display
// RELEVANT FILES: utils/apiErrors.js, components/ui/alert.jsx, form components

'use client';

import React from 'react';
import { AlertTriangle, XCircle, Clock, Shield, Ban, Server, Wifi } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  classifyError,
  getErrorCategoryName,
  shouldTriggerLogout,
  getRetryConfig
} from '@/utils/apiErrors';

/**
 * Enhanced API Error Display Component
 *
 * Displays standardized API errors with appropriate styling and actions
 * Supports field-level errors, retry logic, and proper error classification
 */
export const ApiErrorDisplay = ({
  error,
  onRetry,
  onDismiss,
  showRetry = true,
  showDismiss = true,
  className = '',
  variant = 'destructive'
}) => {
  if (!error) return null;

  const errorCategory = classifyError(error);
  const categoryName = getErrorCategoryName(errorCategory);
  const retryConfig = getRetryConfig(error);

  const getErrorIcon = () => {
    switch (errorCategory) {
      case 'authentication':
        return <Shield className="h-4 w-4" />;
      case 'authorization':
        return <Ban className="h-4 w-4" />;
      case 'rate_limit':
        return <Clock className="h-4 w-4" />;
      case 'server':
        return <Server className="h-4 w-4" />;
      case 'network':
        return <Wifi className="h-4 w-4" />;
      case 'validation':
        return <XCircle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getAlertVariant = () => {
    switch (errorCategory) {
      case 'rate_limit':
      case 'network':
        return 'warning';
      case 'validation':
        return 'default';
      default:
        return variant;
    }
  };

  return (
    <Alert variant={getAlertVariant()} className={className}>
      {getErrorIcon()}
      <AlertTitle className="flex items-center justify-between">
        {categoryName}
        <div className="flex items-center gap-2">
          {error.code && (
            <Badge variant="outline" className="text-xs">
              {error.code}
            </Badge>
          )}
          {error.requestId && (
            <Badge variant="secondary" className="text-xs">
              ID: {error.requestId}
            </Badge>
          )}
          {onDismiss && showDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="h-6 w-6 p-0"
            >
              <XCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      </AlertTitle>
      <AlertDescription>
        <div className="space-y-2">
          <p>{error.message}</p>

          {/* Display field errors if present */}
          {error.fieldErrors && Object.keys(error.fieldErrors).length > 0 && (
            <div className="mt-3 space-y-1">
              <p className="text-sm font-medium">Field Errors:</p>
              {Object.entries(error.fieldErrors).map(([field, fieldError]) => (
                <div key={field} className="text-sm">
                  <span className="font-medium capitalize">{field}:</span> {fieldError}
                </div>
              ))}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-2 mt-3">
            {onRetry && showRetry && retryConfig.shouldRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="text-xs"
              >
                Try Again
              </Button>
            )}

            {shouldTriggerLogout(error) && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.location.href = '/login'}
                className="text-xs"
              >
                Sign In Again
              </Button>
            )}
          </div>
        </div>
      </AlertDescription>
    </Alert>
  );
};

/**
 * Inline Field Error Component
 *
 * Displays field-specific errors for form inputs
 */
export const FieldErrorDisplay = ({ error, fieldName }) => {
  if (!error?.fieldErrors?.[fieldName]) return null;

  return (
    <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
      <XCircle className="h-3 w-3" />
      <span>{error.fieldErrors[fieldName]}</span>
    </div>
  );
};

/**
 * Toast Error Component
 *
 * Simplified error display for toast notifications
 */
export const ToastErrorContent = ({ error }) => {
  const errorCategory = classifyError(error);
  const categoryName = getErrorCategoryName(errorCategory);

  return (
    <div className="flex items-start gap-2">
      <div className="flex-shrink-0 mt-0.5">
        {errorCategory === 'authentication' && <Shield className="h-4 w-4 text-red-500" />}
        {errorCategory === 'authorization' && <Ban className="h-4 w-4 text-red-500" />}
        {errorCategory === 'rate_limit' && <Clock className="h-4 w-4 text-orange-500" />}
        {errorCategory === 'server' && <Server className="h-4 w-4 text-red-500" />}
        {errorCategory === 'network' && <Wifi className="h-4 w-4 text-orange-500" />}
        {errorCategory === 'validation' && <XCircle className="h-4 w-4 text-red-500" />}
        {!['authentication', 'authorization', 'rate_limit', 'server', 'network', 'validation'].includes(errorCategory) && (
          <AlertTriangle className="h-4 w-4 text-red-500" />
        )}
      </div>
      <div className="flex-1">
        <div className="font-medium text-sm">{categoryName}</div>
        <div className="text-xs text-gray-600 mt-1">{error.message}</div>
        {error.code && (
          <Badge variant="outline" className="text-xs mt-1">
            {error.code}
          </Badge>
        )}
      </div>
    </div>
  );
};

/**
 * Form Error Summary Component
 *
 * Displays a summary of all form errors at the top of forms
 */
export const FormErrorSummary = ({ error, onRetry }) => {
  if (!error) return null;

  const hasFieldErrors = error.fieldErrors && Object.keys(error.fieldErrors).length > 0;
  const errorCategory = classifyError(error);

  return (
    <Alert variant="destructive" className="mb-4">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>Form Submission Failed</AlertTitle>
      <AlertDescription>
        <div className="space-y-2">
          <p>{error.message}</p>

          {hasFieldErrors && (
            <div>
              <p className="text-sm font-medium mb-1">Please fix the following issues:</p>
              <ul className="text-sm space-y-1 ml-4">
                {Object.entries(error.fieldErrors).map(([field, fieldError]) => (
                  <li key={field} className="list-disc">
                    <span className="font-medium capitalize">{field}:</span> {fieldError}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {onRetry && errorCategory === 'server' && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="mt-2"
            >
              Try Again
            </Button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
};

/**
 * Loading Error Component
 *
 * Displays errors that occur during data loading/fetching
 */
export const LoadingErrorDisplay = ({ error, onRetry, title = "Failed to load data" }) => {
  if (!error) return null;

  const errorCategory = classifyError(error);
  const retryConfig = getRetryConfig(error);

  return (
    <div className="text-center py-8">
      <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
        <AlertTriangle className="h-6 w-6 text-red-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{error.message}</p>

      {error.code && (
        <Badge variant="outline" className="mb-4">
          Error Code: {error.code}
        </Badge>
      )}

      {onRetry && retryConfig.shouldRetry && (
        <Button onClick={onRetry} variant="outline">
          Try Again
        </Button>
      )}

      {shouldTriggerLogout(error) && (
        <Button
          onClick={() => window.location.href = '/login'}
          variant="outline"
          className="ml-2"
        >
          Sign In Again
        </Button>
      )}
    </div>
  );
};

export default ApiErrorDisplay;