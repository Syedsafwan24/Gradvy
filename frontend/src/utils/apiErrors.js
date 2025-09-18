// Enhanced API error normalization utilities for standardized responses

export function normalizeApiError(err) {
  try {
    // RTK Query style
    const status = err?.status ?? err?.originalStatus ?? 0;
    const data = err?.data ?? err?.error ?? err;
    let message = '';
    const fieldErrors = {};
    let code = data?.code ?? undefined;

    // Handle new standardized error format
    if (data && data.success === false && data.error) {
      const errorObj = data.error;
      message = errorObj.message || 'An error occurred';
      code = errorObj.code;

      // Extract field errors from standardized format
      if (errorObj.field_errors && typeof errorObj.field_errors === 'object') {
        Object.assign(fieldErrors, errorObj.field_errors);
      }

      // Handle additional details if present
      if (errorObj.details && typeof errorObj.details === 'object') {
        // Check if details contain general errors
        if (errorObj.details.general_errors && Array.isArray(errorObj.details.general_errors)) {
          if (!message || message === 'An error occurred') {
            message = errorObj.details.general_errors[0] || message;
          }
        }
      }
    }
    // Handle legacy DRF format and string responses
    else if (typeof data === 'string') {
      message = data;
    } else if (data) {
      // Common DRF keys (legacy support)
      if (typeof data.detail === 'string') message = data.detail;
      else if (typeof data.message === 'string') message = data.message;
      else if (typeof data.error === 'string') message = data.error;
      else if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
        message = data.non_field_errors.join(' ');
      }

      // Helper to collect flat field errors (legacy support)
      const collectFieldErrors = (obj) => {
        if (!obj || typeof obj !== 'object') return;
        Object.keys(obj).forEach((k) => {
          const v = obj[k];
          if (Array.isArray(v) && v.length && typeof v[0] === 'string') {
            fieldErrors[k] = v.join(' ');
          } else if (v && typeof v === 'object') {
            // Nesting (rare) -> flatten depth-1
            Object.keys(v).forEach((innerK) => {
              const innerV = v[innerK];
              if (Array.isArray(innerV) && innerV.length && typeof innerV[0] === 'string') {
                fieldErrors[innerK] = innerV.join(' ');
              }
            });
          }
        });
      };

      // Only collect field errors if not already processed from standardized format
      if (Object.keys(fieldErrors).length === 0) {
        collectFieldErrors(data);
        if (data.errors) collectFieldErrors(data.errors);
      }

      // If still no message, use the first field error or fallback
      if (!message) {
        const firstField = Object.keys(fieldErrors)[0];
        if (firstField) message = fieldErrors[firstField];
      }
      // If message looks generic ("failed"), prefer first field error
      if (message && /failed|error/i.test(message) && Object.keys(fieldErrors).length) {
        const firstField = Object.keys(fieldErrors)[0];
        if (firstField) message = fieldErrors[firstField];
      }
    }

    if (!message) {
      // Last resort fallback, but still include status
      message = status ? `Request failed (HTTP ${status})` : 'Request failed';
    }

    return {
      status,
      code,
      message,
      fieldErrors,
      // Add metadata for debugging
      isStandardFormat: data && data.success === false,
      requestId: data?.meta?.request_id
    };
  } catch (e) {
    return { status: 0, message: 'Unexpected error', fieldErrors: {} };
  }
}

// Apply field errors to react-hook-form's setError
export function applyFieldErrorsToForm(normalized, setError) {
  if (!normalized?.fieldErrors) return;
  Object.entries(normalized.fieldErrors).forEach(([field, msg]) => {
    // Map DRF non_field_errors to root
    const name = field === 'non_field_errors' ? 'root' : field;
    try {
      setError(name, { type: 'server', message: msg });
    } catch {}
  });
}

// Enhanced helper to extract user-friendly messages
export function getTopLevelMessage(normalized) {
  return normalized?.message || 'An error occurred';
}

// Helper to check if response is successful
export function isSuccessResponse(response) {
  return response?.data?.success === true;
}

// Helper to extract success data
export function extractSuccessData(response) {
  if (isSuccessResponse(response)) {
    return response.data.data;
  }
  return response?.data || response;
}

// Helper to extract success message
export function extractSuccessMessage(response) {
  if (isSuccessResponse(response)) {
    return response.data.message || 'Operation completed successfully';
  }
  return 'Operation completed successfully';
}

// Enhanced error classification
export function classifyError(normalized) {
  const { status, code } = normalized;

  // Use error code for precise classification
  if (code) {
    switch (code) {
      case 'INVALID_CREDENTIALS':
      case 'TOKEN_EXPIRED':
      case 'INVALID_TOKEN':
        return 'authentication';
      case 'INSUFFICIENT_PERMISSIONS':
        return 'authorization';
      case 'VALIDATION_ERROR':
      case 'REQUIRED_FIELD_MISSING':
      case 'INVALID_INPUT_FORMAT':
        return 'validation';
      case 'RESOURCE_NOT_FOUND':
        return 'not_found';
      case 'RESOURCE_CONFLICT':
      case 'DUPLICATE_ENTRY':
        return 'conflict';
      case 'RATE_LIMIT_EXCEEDED':
        return 'rate_limit';
      case 'MFA_REQUIRED':
      case 'INVALID_MFA_CODE':
        return 'mfa';
      case 'INTERNAL_ERROR':
      case 'SERVICE_UNAVAILABLE':
        return 'server';
      default:
        break;
    }
  }

  // Fallback to status-based classification
  if (status >= 400 && status < 500) {
    if (status === 401) return 'authentication';
    if (status === 403) return 'authorization';
    if (status === 404) return 'not_found';
    if (status === 409) return 'conflict';
    if (status === 422) return 'validation';
    if (status === 429) return 'rate_limit';
    return 'client';
  }

  if (status >= 500) {
    return 'server';
  }

  return 'unknown';
}

// Get user-friendly error category name
export function getErrorCategoryName(category) {
  const categoryNames = {
    authentication: 'Authentication Error',
    authorization: 'Access Denied',
    validation: 'Validation Error',
    not_found: 'Not Found',
    conflict: 'Conflict',
    rate_limit: 'Rate Limit Exceeded',
    mfa: 'Multi-Factor Authentication',
    server: 'Server Error',
    client: 'Request Error',
    network: 'Network Error',
    unknown: 'Error'
  };

  return categoryNames[category] || 'Error';
}

// Check if error should trigger logout
export function shouldTriggerLogout(normalized) {
  const { code, status } = normalized;

  // Token-related errors that require re-authentication
  const logoutCodes = [
    'TOKEN_EXPIRED',
    'INVALID_TOKEN',
    'INVALID_CREDENTIALS'
  ];

  return logoutCodes.includes(code) || status === 401;
}

// Get retry configuration for error
export function getRetryConfig(normalized) {
  const { code, status } = normalized;

  // Don't retry authentication/authorization errors
  if (status === 401 || status === 403) {
    return { shouldRetry: false, maxRetries: 0 };
  }

  // Don't retry validation errors
  if (status === 400 || status === 422 || code === 'VALIDATION_ERROR') {
    return { shouldRetry: false, maxRetries: 0 };
  }

  // Rate limit - retry with backoff
  if (status === 429 || code === 'RATE_LIMIT_EXCEEDED') {
    return { shouldRetry: true, maxRetries: 3, backoffMultiplier: 2 };
  }

  // Server errors - retry with limited attempts
  if (status >= 500) {
    return { shouldRetry: true, maxRetries: 2, backoffMultiplier: 1.5 };
  }

  // Network errors - retry aggressively
  if (status === 0 || !status) {
    return { shouldRetry: true, maxRetries: 3, backoffMultiplier: 1.2 };
  }

  return { shouldRetry: false, maxRetries: 0 };
}
