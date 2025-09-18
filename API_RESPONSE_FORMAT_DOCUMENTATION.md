# Gradvy API Response Format Documentation

## Overview

This document describes the standardized API response format implemented across all Gradvy API endpoints. The new format provides consistent error handling, proper status codes, and enhanced debugging capabilities for both frontend and backend development.

## Response Format Structure

### Success Response Format

All successful API responses follow this standardized structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Actual response data
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### Error Response Format

All error responses follow this standardized structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly error message",
    "details": {
      // Additional error context
    },
    "field_errors": {
      "field_name": ["Field-specific error message"]
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_abc123"
  }
}
```

## Response Fields

### Common Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `meta` | object | Metadata about the response |
| `meta.timestamp` | string | ISO 8601 timestamp of the response |
| `meta.request_id` | string | Unique identifier for the request |

### Success Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | User-friendly success message |
| `data` | any | The actual response payload |

### Error Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `error` | object | Error information |
| `error.code` | string | Machine-readable error code |
| `error.message` | string | User-friendly error message |
| `error.details` | object | Additional error context (optional) |
| `error.field_errors` | object | Field-specific validation errors (optional) |

## Standard Error Codes

### Authentication & Authorization

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `ACCOUNT_LOCKED` | 429 | Account temporarily locked |
| `MFA_REQUIRED` | 202 | Multi-factor authentication required |
| `INVALID_MFA_CODE` | 400 | Invalid or expired MFA code |
| `INVALID_TOKEN` | 401 | Invalid or malformed token |
| `TOKEN_EXPIRED` | 401 | Token has expired |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |

### Validation

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | General validation error |
| `REQUIRED_FIELD_MISSING` | 400 | Required field is missing |
| `INVALID_INPUT_FORMAT` | 400 | Input format is invalid |
| `DUPLICATE_ENTRY` | 409 | Resource already exists |

### Business Logic

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `RESOURCE_CONFLICT` | 409 | Resource conflict |
| `OPERATION_NOT_ALLOWED` | 400 | Operation not permitted |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |

### System

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `EXTERNAL_SERVICE_ERROR` | 502 | External service error |

## Example Responses

### Successful Login

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 123,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### MFA Required

```json
{
  "success": true,
  "message": "Multi-factor authentication required",
  "data": {
    "mfa_token": "temp_mfa_token_123",
    "mfa_required": true
  },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_abc124"
  }
}
```

### Validation Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "general_errors": ["Password must contain at least one uppercase letter"]
    },
    "field_errors": {
      "email": ["Enter a valid email address"],
      "password": ["Password must be at least 8 characters"]
    }
  },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_abc125"
  }
}
```

### Resource Not Found

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User preferences not found. Please complete onboarding first",
    "details": {
      "onboarding_required": true
    }
  },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_abc126"
  }
}
```

### Internal Server Error

```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred while processing your request",
    "details": {
      "exception_type": "DatabaseConnectionError"
    }
  },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_abc127"
  }
}
```

## Implementation Guide

### Backend Implementation

#### Using StandardAPIResponse Classes

```python
from utils.responses import APISuccess, APIError, AuthAPIResponse

# Success response
return APISuccess.create(
    data=serializer.data,
    message="User profile updated successfully"
)

# Error response
return APIError.bad_request(
    message="Invalid input provided",
    code=ErrorCodes.VALIDATION_ERROR,
    field_errors={"email": ["Invalid email format"]}
)

# Specialized auth response
return AuthAPIResponse.login_success(
    user_data=user_data,
    tokens=tokens,
    message="Login successful"
)
```

#### Error Handling

```python
try:
    # Your business logic here
    result = perform_operation()
    return APISuccess.create(data=result)
except ValidationError as e:
    return APIValidationError.create_from_serializer(serializer)
except Exception as e:
    return handle_exception(e, "Operation failed")
```

### Frontend Implementation

#### Error Handling

```javascript
import { normalizeApiError, classifyError } from '@/utils/apiErrors';

try {
  const response = await api.getData();
  // Handle successful response
  const data = extractSuccessData(response);
} catch (error) {
  const normalizedError = normalizeApiError(error);
  const errorCategory = classifyError(normalizedError);

  // Display appropriate error message
  console.error('API Error:', normalizedError.message);

  // Handle field errors
  if (normalizedError.fieldErrors) {
    Object.entries(normalizedError.fieldErrors).forEach(([field, message]) => {
      setFieldError(field, message);
    });
  }
}
```

#### Error Display Components

```jsx
import { ApiErrorDisplay } from '@/components/error/ApiErrorDisplay';

function MyComponent() {
  const [error, setError] = useState(null);

  return (
    <div>
      {error && (
        <ApiErrorDisplay
          error={error}
          onRetry={() => retryOperation()}
          onDismiss={() => setError(null)}
        />
      )}
      {/* Your component content */}
    </div>
  );
}
```

## Migration Guide

### For Existing APIs

1. **Backend**: Update all API endpoints to use the new `StandardAPIResponse` classes
2. **Frontend**: Update error handling to use the new `normalizeApiError` function
3. **Components**: Replace hardcoded error messages with server-provided messages

### Breaking Changes

- **Response Structure**: All responses now include `success`, `message`, and `meta` fields
- **Error Format**: Errors are now nested under an `error` object
- **Field Errors**: Validation errors are now under `error.field_errors`

### Backward Compatibility

The `normalizeApiError` function includes fallback logic to handle legacy response formats during the transition period.

## Best Practices

### Backend Development

1. Always use the standardized response classes
2. Provide meaningful error messages for users
3. Include appropriate error codes for client-side handling
4. Use field-specific errors for validation issues
5. Include context in error details when helpful

### Frontend Development

1. Always normalize API errors before displaying
2. Use server-provided error messages instead of hardcoded ones
3. Display field errors next to relevant form fields
4. Implement appropriate retry logic based on error type
5. Log errors with request IDs for debugging

### Error Messages

1. **Be User-Friendly**: Write errors that non-technical users can understand
2. **Be Actionable**: Tell users what they can do to fix the issue
3. **Be Specific**: Provide enough detail to help users resolve the problem
4. **Be Consistent**: Use similar language and tone across all errors

## Testing

### Backend Testing

```python
def test_api_response_format(self):
    response = self.client.post('/api/endpoint/', data)

    # Test success response
    self.assertTrue(response.data['success'])
    self.assertIn('message', response.data)
    self.assertIn('data', response.data)
    self.assertIn('meta', response.data)

    # Test error response
    response = self.client.post('/api/endpoint/', invalid_data)
    self.assertFalse(response.data['success'])
    self.assertIn('error', response.data)
    self.assertIn('code', response.data['error'])
    self.assertIn('message', response.data['error'])
```

### Frontend Testing

```javascript
describe('API Error Handling', () => {
  it('should normalize API errors correctly', () => {
    const apiError = {
      status: 400,
      data: {
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid input',
          field_errors: { email: ['Invalid email'] }
        }
      }
    };

    const normalized = normalizeApiError(apiError);

    expect(normalized.message).toBe('Invalid input');
    expect(normalized.code).toBe('VALIDATION_ERROR');
    expect(normalized.fieldErrors.email).toBe('Invalid email');
  });
});
```

## Monitoring and Analytics

### Error Tracking

- Use request IDs to track errors across systems
- Monitor error rates by error code
- Track field validation error frequency
- Alert on high error rates for specific endpoints

### Metrics to Track

1. **Error Rate**: Percentage of requests resulting in errors
2. **Error Distribution**: Breakdown by error code
3. **Field Error Frequency**: Most common validation errors
4. **Response Time**: Including error response times
5. **Retry Success Rate**: Success rate of retried requests

## Conclusion

This standardized API response format provides:

- **Consistency**: All APIs follow the same response structure
- **Better UX**: Clear, actionable error messages from the server
- **Improved Debugging**: Request IDs and detailed error information
- **Enhanced Monitoring**: Structured data for analytics and alerting
- **Developer Experience**: Predictable error handling patterns

By following this format, we ensure a professional, user-friendly API that provides excellent developer and user experiences.

---

**Document Version**: 1.0
**Last Updated**: January 2024
**Authors**: Claude Code Implementation Team
**Status**: Active Implementation