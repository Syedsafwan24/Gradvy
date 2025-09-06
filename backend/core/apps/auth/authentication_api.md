# User Login API

> **URL:** `POST /api/auth/login/`
>
> **Permissions:** `AllowAny`

## Description

Authenticates a user with their email and password. If successful, it returns JWT access and refresh tokens. If MFA is enabled for the user, it will return a message indicating that the second factor is required.

---

## Request

### Body

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

---

## Responses

### ✅ Success Response (No MFA)

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

### ✅ Success Response (MFA Required)

- **Code:** `200 OK`
- **Content:**

```json
{
    "mfa_required": true,
    "message": "MFA verification required"
}
```

### ❌ Error Responses

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
