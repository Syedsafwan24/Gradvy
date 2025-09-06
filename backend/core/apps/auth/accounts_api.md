# Accounts Module API Endpoints

This document details all the API endpoints provided by the `accounts` module.

---

## 1. User Login API

> **URL:** `POST /api/auth/login/`
>
> **Permissions:** `AllowAny`

### Description

Authenticates a user with their email and password. If successful, it returns JWT access and refresh tokens. If MFA is enabled for the user, it will return a message indicating that the second factor is required.

### Request

#### Body

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `email` | string | Yes | The user's registered email address. |
| `password` | string | Yes | The user's password. |

#### Example Request Body

```json
{
  "email": "testuser@example.com",
  "password": "Str0ngP@ssw0rd!"
}
```

### Responses

#### ✅ Success Response (No MFA)

- **Code:** `200 OK`
- **Content:**

```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2023-10-27T10:00:00Z",
        "last_login": "2023-10-27T12:00:00Z",
        "profile": {
            "department": "Engineering",
            "position": "Software Developer",
            "phone_number": "123-456-7890"
        },
        "groups": [],
        "groups": []
    }
}
```

#### ✅ Success Response (MFA Required)

- **Code:** `200 OK`
- **Content:**

```json
{
    "mfa_required": true,
    "message": "MFA verification required"
}
```

#### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** The provided credentials are invalid, the account is disabled, or the account is locked.
    - **Content:**
      ```json
      {
        "detail": "Invalid credentials"
      }
      ```

*   **Code:** `401 Unauthorized`
    - **Reason:** This endpoint is public, so this error is not expected unless there is a global authentication policy misconfiguration.

---

## 2. Token Refresh API

> **URL:** `POST /api/auth/refresh/`
>
> **Permissions:** `AllowAny`

### Description

Obtains a new access token using a valid refresh token. This is used to keep user sessions alive without requiring re-authentication.

### Request

#### Body

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `refresh` | string | Yes | The refresh token obtained during login. |

#### Example Request Body

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Responses

#### ✅ Success Response

- **Code:** `200 OK`
- **Content:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### ❌ Error Responses

*   **Code:** `401 Unauthorized`
    - **Reason:** The refresh token is invalid or expired.
    - **Content:**
      ```json
      {
        "detail": "Token is invalid or expired",
        "code": "token_not_valid"
      }
      ```

---

## 3. User Profile API

> **URL:** `GET /api/auth/me/`
> **URL:** `PUT /api/auth/me/`
>
> **Permissions:** `IsAuthenticated`

### Description

Retrieves the profile information of the currently authenticated user (GET request) or updates it (PUT request).

### Request

#### GET Request

- **Body:** None

#### PUT Request

- **Body:** Partial user and profile data can be sent for updates.

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `email` | string | No | The user's email address. |
| `first_name` | string | No | The user's first name. |
| `last_name` | string | No | The user's last name. |
| `profile.department` | string | No | The user's department. |
| `profile.position` | string | No | The user's position. |
| `profile.phone_number` | string | No | The user's phone number. |

#### Example PUT Request Body

```json
{
  "first_name": "Jane",
  "profile": {
    "department": "HR"
  }
}
```

### Responses

#### ✅ Success Response (GET & PUT)

- **Code:** `200 OK`
- **Content:**

```json
{
    "id": 1,
    "email": "testuser@example.com",
    "first_name": "Test",
    "last_name": "User",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2023-10-27T10:00:00Z",
    "last_login": "2023-10-27T12:00:00Z",
    "profile": {
        "department": "Engineering",
        "position": "Software Developer",
        "phone_number": "123-456-7890"
    },
    "groups": [],
    "modules": ["ESS"]
}
```

#### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** Invalid data provided in the request body.
    - **Content:**
      ```json
      {
        "email": [
          "Enter a valid email address."
        ]
      }
      ```

*   **Code:** `401 Unauthorized`
    - **Reason:** Authentication credentials were not provided or are invalid.

---

## 4. Password Change API

> **URL:** `POST /api/auth/password/change/`
>
> **Permissions:** `IsAuthenticated`

### Description

Allows an authenticated user to change their password.

### Request

#### Body

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `current_password` | string | Yes | The user's current password. |
| `new_password` | string | Yes | The new password for the user. |

#### Example Request Body

```json
{
  "current_password": "OldP@ssw0rd!",
  "new_password": "NewStr0ngP@ssw0rd!"
}
```

### Responses

#### ✅ Success Response

- **Code:** `200 OK`
- **Content:**

```json
{
  "message": "Password changed successfully"
}
```

#### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** Current password is incorrect, or the new password does not meet validation requirements.
    - **Content:**
      ```json
      {
        "current_password": [
          "Current password is incorrect"
        ]
      }
      ```

*   **Code:** `401 Unauthorized`
    - **Reason:** Authentication credentials were not provided or are invalid.

---

## 5. MFA Enrollment API

> **URL:** `POST /api/auth/mfa/enroll/` (Initiate Enrollment)
> **URL:** `PUT /api/auth/mfa/enroll/` (Confirm Enrollment)
>
> **Permissions:** `IsAuthenticated`

### Description

Initiates the MFA enrollment process by generating a TOTP secret and QR code (POST request). Confirms the MFA enrollment with a provided code (PUT request).

### Request

#### POST Request (Initiate Enrollment)

- **Body:** None

#### PUT Request (Confirm Enrollment)

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `device_id` | integer | Yes | The ID of the TOTP device generated during initiation. |
| `code` | string | Yes | The 6-digit code from the authenticator app. |

#### Example PUT Request Body

```json
{
  "device_id": 1,
  "code": "123456"
}
```

### Responses

#### ✅ Success Response (POST - Initiate Enrollment)

- **Code:** `200 OK`
- **Content:**

```json
{
  "secret": "[TOTP_SECRET_KEY]",
  "qr_code": "data:image/png;base64,[BASE64_ENCODED_QR_CODE]",
  "backup_codes": [
    "ABCDEFGH",
    "IJKLMNOP",
    ...
  ],
  "device_id": 1
}
```

#### ✅ Success Response (PUT - Confirm Enrollment)

- **Code:** `200 OK`
- **Content:**

```json
{
  "message": "MFA enrolled successfully"
}
```

#### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** Invalid code provided during confirmation, or device not found.
    - **Content:**
      ```json
      {
        "error": "Invalid code"
      }
      ```

*   **Code:** `401 Unauthorized`
    - **Reason:** Authentication credentials were not provided or are invalid.

---

## 6. MFA Verify API

> **URL:** `POST /api/auth/mfa/verify/`
>
> **Permissions:** `AllowAny` (but requires a pending user ID in session)

### Description

Verifies the MFA code provided by the user after a successful initial login when MFA is enabled.

### Request

#### Body

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `code` | string | Yes | The 6-digit code from the authenticator app or a backup code. |

#### Example Request Body

```json
{
  "code": "123456"
}
```

### Responses

#### ✅ Success Response

- **Code:** `200 OK`
- **Content:**

```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2023-10-27T10:00:00Z",
        "last_login": "2023-10-27T12:00:00Z",
        "profile": {
            "department": "Engineering",
            "position": "Software Developer",
            "phone_number": "123-456-7890"
        },
        "groups": [],
        "groups": []
    }
}
```

#### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** Invalid MFA code, no pending authentication session, or no MFA device found for the user.
    - **Content:**
      ```json
      {
        "error": "Invalid MFA code"
      }
      ```

---

## 7. Logout API

> **URL:** `POST /api/auth/logout/`
>
> **Permissions:** `IsAuthenticated`

### Description

Blacklists the provided refresh token, effectively logging the user out and invalidating all associated access tokens.

### Request

#### Body

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `refresh` | string | Yes | The refresh token to be blacklisted. |

#### Example Request Body

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Responses

#### ✅ Success Response

- **Code:** `200 OK`
- **Content:** (Empty response body)

#### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** Invalid refresh token provided.
    - **Content:**
      ```json
      {
        "detail": "Token is blacklisted",
        "code": "token_not_valid"
      }
      ```

*   **Code:** `401 Unauthorized`
    - **Reason:** Authentication credentials were not provided or are invalid.
