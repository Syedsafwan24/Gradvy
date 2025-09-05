# [Endpoint Title]

> **URL:** `[HTTP Method] /api/path/to/endpoint/`
>
> **Permissions:** `[e.g., AllowAny, IsAuthenticated]`

## Description

[A clear and concise description of what this endpoint does.]

---

## Request

### Body

| Field | Type | Required | Description |
| :---- | :--- | :--- | :--- |
| `field_1` | string | Yes | [Description of field_1] |
| `field_2` | integer | No | [Description of field_2] |

#### Example Request Body

```json
{
  "field_1": "value",
  "field_2": 123
}
```

---

## Responses

### ✅ Success Response

- **Code:** `200 OK`
- **Content:**

```json
{
  "message": "Success!",
  "data": {
    "key": "value"
  }
}
```

### ❌ Error Responses

*   **Code:** `400 Bad Request`
    - **Reason:** [Explanation of why this error would occur, e.g., "Invalid input data"]
    - **Content:**
      ```json
      {
        "error": "A descriptive error message."
      }
      ```

*   **Code:** `401 Unauthorized`
    - **Reason:** [e.g., "Authentication credentials were not provided."]
    - **Content:**
      ```json
      {
        "detail": "Authentication credentials were not provided."
      }
      ```

*   **Code:** `403 Forbidden`
    - **Reason:** [e.g., "User does not have permission to perform this action."]
    - **Content:**
      ```json
      {
        "detail": "You do not have permission to perform this action."
      }
      ```
