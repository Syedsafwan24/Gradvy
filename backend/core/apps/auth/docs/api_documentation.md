# Gradvy Authentication API Documentation

## Overview

This document provides comprehensive documentation for the Gradvy Authentication API. The API provides secure authentication services with Multi-Factor Authentication (MFA) support.

**Base URL**: `http://localhost:8000/api/auth/`

**Authentication**: JWT Token-based authentication

---

## Authentication Endpoints

### 1. User Login

**Endpoint**: `POST /api/auth/login/`  
**Permission**: `AllowAny`

Authenticates a user with email and password. Returns JWT tokens or MFA challenge.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

#### Success Response (No MFA)

**Status**: `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2023-10-27T10:00:00Z",
    "last_login": "2023-10-27T12:00:00Z",
    "mfa_enrolled": false,
    "profile": {
      "phone_number": "+1234567890"
    },
    "groups": []
  }
}
```

#### Success Response (MFA Required)

**Status**: `200 OK`

```json
{
  "mfa_required": true,
  "mfa_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "MFA verification required"
}
```

#### Error Responses

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| `401` | `INVALID_CREDENTIALS` | Invalid email or password |
| `403` | `ACCOUNT_DISABLED` | User account is disabled |
| `429` | `ACCOUNT_LOCKED` | Account locked due to failed attempts |

---

### 2. MFA Verification

**Endpoint**: `POST /api/auth/mfa/verify/`  
**Permission**: `AllowAny`

Verifies MFA code and completes authentication process.

#### Request Body

```json
{
  "mfa_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "code": "123456"
}
```

#### Success Response

**Status**: `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "mfa_enrolled": true,
    "groups": []
  }
}
```

#### Error Responses

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| `400` | `MFA_INVALID_CODE` | Invalid MFA code |
| `400` | `MFA_EXPIRED_TOKEN` | MFA token expired |
| `400` | `MFA_DEVICE_NOT_FOUND` | No MFA device found |

---

### 3. Token Refresh

**Endpoint**: `POST /api/auth/token/refresh/`  
**Permission**: `AllowAny`

Refreshes access token using refresh token.

#### Request Body

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Success Response

**Status**: `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 4. User Logout

**Endpoint**: `POST /api/auth/logout/`  
**Permission**: `IsAuthenticated`

Logs out user by blacklisting refresh token.

#### Request Body

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Success Response

**Status**: `200 OK` (Empty response)

---

## Profile Management

### 5. Get/Update Profile

**Endpoint**: `GET/PUT /api/auth/profile/`  
**Permission**: `IsAuthenticated`

Retrieve or update user profile information.

#### GET Response

**Status**: `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_staff": false,
  "date_joined": "2023-10-27T10:00:00Z",
  "last_login": "2023-10-27T12:00:00Z",
  "mfa_enrolled": false,
  "profile": {
    "phone_number": "+1234567890"
  },
  "groups": []
}
```

#### PUT Request Body

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "phone_number": "+1234567890"
  }
}
```

---

### 6. Change Password

**Endpoint**: `POST /api/auth/password/change/`  
**Permission**: `IsAuthenticated`

Changes user password.

#### Request Body

```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword123"
}
```

#### Success Response

**Status**: `200 OK`

```json
{
  "message": "Password changed successfully"
}
```

#### Error Responses

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| `400` | `VALIDATION_ERROR` | Current password incorrect |

---

## Multi-Factor Authentication

### 7. MFA Enrollment

**Endpoint**: `POST /api/auth/mfa/enroll/`  
**Permission**: `IsAuthenticated`

Initiates MFA enrollment process.

#### Success Response

**Status**: `200 OK`

```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "backup_codes": [
    "ABC12DEF",
    "GHI34JKL",
    "MNO56PQR"
  ],
  "device_id": 1
}
```

---

### 8. Confirm MFA Enrollment

**Endpoint**: `PUT /api/auth/mfa/enroll/`  
**Permission**: `IsAuthenticated`

Confirms MFA enrollment with verification code.

#### Request Body

```json
{
  "device_id": 1,
  "code": "123456"
}
```

#### Success Response

**Status**: `200 OK`

```json
{
  "message": "MFA enrolled successfully"
}
```

---

### 9. Disable MFA

**Endpoint**: `POST /api/auth/mfa/disable/`  
**Permission**: `IsAuthenticated`

Disables MFA for the user account.

#### Success Response

**Status**: `200 OK`

```json
{
  "message": "MFA disabled successfully"
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE_CONSTANT"
}
```

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `PERMISSION_DENIED` | Insufficient permissions |
| `ACCOUNT_LOCKED` | Account temporarily locked |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL_ERROR` | Server error occurred |
| `INVALID_CREDENTIALS` | Login credentials invalid |
| `MFA_REQUIRED` | MFA verification needed |
| `MFA_INVALID_CODE` | MFA code incorrect |
| `MFA_EXPIRED_TOKEN` | MFA token expired |

---

## Authentication Headers

All authenticated endpoints require JWT token in header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| Login | 5 attempts | 15 minutes |
| MFA Verify | 10 attempts | 5 minutes |
| Password Change | 3 attempts | 1 hour |

---

## Examples

### Complete Authentication Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 2. If MFA required, verify code
curl -X POST http://localhost:8000/api/auth/mfa/verify/ \
  -H "Content-Type: application/json" \
  -d '{"mfa_token": "token", "code": "123456"}'

# 3. Access protected resource
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer access_token"

# 4. Refresh token when needed
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "refresh_token"}'

# 5. Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer access_token" \
  -d '{"refresh": "refresh_token"}'
```

### MFA Setup Flow

```bash
# 1. Enroll in MFA
curl -X POST http://localhost:8000/api/auth/mfa/enroll/ \
  -H "Authorization: Bearer access_token"

# 2. Confirm enrollment with TOTP code
curl -X PUT http://localhost:8000/api/auth/mfa/enroll/ \
  -H "Authorization: Bearer access_token" \
  -H "Content-Type: application/json" \
  -d '{"device_id": 1, "code": "123456"}'

# 3. Disable MFA (if needed)
curl -X POST http://localhost:8000/api/auth/mfa/disable/ \
  -H "Authorization: Bearer access_token"
```

---

## Security Considerations

1. **HTTPS Required**: Always use HTTPS in production
2. **Token Storage**: Store JWT tokens securely (HttpOnly cookies recommended)
3. **Token Rotation**: Implement token rotation for enhanced security
4. **Rate Limiting**: Implement proper rate limiting
5. **Input Validation**: All inputs are validated server-side
6. **Audit Logging**: All authentication events are logged

---

## SDKs and Libraries

### JavaScript/TypeScript

```javascript
// Example using axios
const api = axios.create({
  baseURL: 'http://localhost:8000/api/auth/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login function
async function login(email, password) {
  const response = await api.post('login/', { email, password });
  if (response.data.mfa_required) {
    // Handle MFA flow
    return { mfa_required: true, mfa_token: response.data.mfa_token };
  }
  // Store tokens
  localStorage.setItem('access_token', response.data.access);
  localStorage.setItem('refresh_token', response.data.refresh);
  return response.data;
}
```

### Python

```python
import requests

class GradyAuthClient:
    def __init__(self, base_url="http://localhost:8000/api/auth/"):
        self.base_url = base_url
        self.access_token = None
    
    def login(self, email, password):
        response = requests.post(f"{self.base_url}login/", {
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            if data.get('mfa_required'):
                return {'mfa_required': True, 'mfa_token': data['mfa_token']}
            self.access_token = data['access']
            return data
        response.raise_for_status()
    
    def get_profile(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}profile/", headers=headers)
        return response.json()
```

---

This API follows REST principles and provides comprehensive authentication services with enterprise-grade security features.