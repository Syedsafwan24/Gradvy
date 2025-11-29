# Gradvy Authentication Flow (Login & Registration)

## System Overview
- `backend/core/core/urls.py:7` mounts the authentication API at `/api/auth/`, delegating to `apps.auth.api.urls` for all auth-related endpoints.
- `backend/core/apps/auth/api/urls.py:6` wires concrete routes for `register/`, `login/`, `logout/`, token refresh, MFA utilities, and profile management.
- `backend/core/core/settings.py:82` declares the custom user model (`gradvy_auth.User`) and configures DRF + Simple JWT (`backend/core/core/settings.py:150` and `backend/core/core/settings.py:174`) so JWT auth runs alongside Django sessions and CSRF protections.
- `backend/core/utils/responses.py:289` standardizes auth responses (wrapping payloads under `success/message/data/meta`), which the frontend expects when parsing results and errors.

## Frontend Implementation

### Shared API & State Infrastructure
- `frontend/src/store/api/authApi.js:7` defines the RTK Query slice with `baseUrl` derived from the Next.js config (`frontend/src/config/api.js:1`) and `credentials: 'include'` so the httpOnly refresh cookie travels automatically.
- `frontend/src/store/api/authApi.js:11` injects the in-memory access token into `Authorization` headers and attaches `X-CSRFToken` from cookies via `getCSRFToken` (`frontend/src/lib/cookieUtils.js:7`).
- `frontend/src/store/api/authApi.js:46` decorates the base query to auto-refresh access tokens when a 401 occurs, queueing concurrent requests and re-dispatching `setAccessToken`.
- Successful `login` and `register` mutations (`frontend/src/store/api/authApi.js:123` and `frontend/src/store/api/authApi.js:160`) unwrap the standardized response, extract `access_token`/`refresh_token`, and dispatch `setCredentials` (`frontend/src/store/slices/authSlice.js:24`) so Redux holds the access token and user payload.
- `frontend/src/store/slices/authSlice.js:200` exposes selectors that drive auto-refresh logic; `AuthInitializer` (`frontend/src/components/auth/AuthInitializer.jsx:37`) runs on app boot to restore the session by hitting `/api/auth/refresh/` when Redux has a user but stale tokens.
- CSRF cookie handling lives in `frontend/src/components/auth/AuthInitializer.jsx:52` (manual fetch) and `frontend/src/store/api/authApi.js:19`, ensuring mutation requests satisfy Django’s CSRF checks when necessary.

### Login UI + UX
- `frontend/src/app/login/page.jsx:19` defines Yup validation for email, password, and optional `remember_me` toggle before submitting through React Hook Form (`frontend/src/app/login/page.jsx:51`).
- Submission flows through `useLoginMutation` (`frontend/src/app/login/page.jsx:48`), calling `POST /api/auth/login/` with the form payload (`frontend/src/app/login/page.jsx:115`).
- The component distinguishes MFA-required responses vs immediate success (`frontend/src/app/login/page.jsx:119`), storing the backend-issued `mfa_token` in state for the follow-up step.
- The MFA view leverages `useVerifyMFAMutation` (`frontend/src/app/login/page.jsx:49`) to submit the 6-digit code plus `mfa_token` (`frontend/src/app/login/page.jsx:135`); on success the shared mutation handler has already populated Redux, and the page redirects to `/app/dashboard`.
- Errors funnel through `normalizeApiError` utilities (`frontend/src/utils/apiErrors.js:6`), letting the page highlight field-level problems coming from DRF serializers.

### Registration UI
- `frontend/src/app/register/page.jsx:19` enforces names, email, password strength, and matching confirmation before invoking `useRegisterMutation` (`frontend/src/app/register/page.jsx:51`).
- `onSubmit` (`frontend/src/app/register/page.jsx:83`) posts first/last name, email, and both password fields; the mutation’s shared handler stores the returned tokens/user state and the page redirects to onboarding.
- Validation feedback again relies on `normalizeApiError` (`frontend/src/app/register/page.jsx:95`) so server-side uniqueness errors surface inline.

## Backend Implementation

### Serializers & Validation
- `backend/core/apps/auth/api/serializers.py:108` authenticates via `django.contrib.auth.authenticate`, ensuring both credentials are present and the user is active before attaching the `user` object for downstream use. The optional `remember_me` flag survives validation for cookie lifetime decisions.
- `backend/core/apps/auth/api/serializers.py:150` enforces unique email addresses and Django’s password validators, then delegates to `User.objects.create_user` to hash and persist the new account.

### Authentication Views
- `backend/core/apps/auth/api/views.py:39` drives the login flow: it validates input, checks `user.mfa_enrolled` (`backend/core/apps/auth/api/views.py:48`), and either issues an MFA challenge token or finalizes the login via `_complete_login`.
- `_complete_login` (`backend/core/apps/auth/api/views.py:98`) creates SimpleJWT refresh/access tokens, extends refresh lifetime when `remember_me=True`, serializes the user via `UserSerializer`, and sets the refresh token in an httpOnly cookie (`backend/core/apps/auth/api/views.py:124`).
- `backend/core/apps/auth/api/views.py:140` handles TOTP verification by decoding the transient `mfa_token`, confirming a device with `django_otp`, and reusing `_complete_login` so the post-MFA experience matches the direct login path.
- `backend/core/apps/auth/api/views.py:655` manages registration: after serializer validation it creates the user, issues tokens, responds with `AuthAPIResponse.login_success`, and seeds the refresh cookie for immediate authentication (`backend/core/apps/auth/api/views.py:685`).
- Refreshing access tokens happens through `CookieTokenRefreshView` (`backend/core/apps/auth/api/views.py:384`), which reads the refresh token from the cookie, validates it with SimpleJWT, and returns a new access token (respecting rotation settings) while maintaining the response envelope.

### Supporting Infrastructure
- `backend/core/utils/responses.py:289` formats every success/error, which is why the frontend’s RTK query layer peels off `data` from the response.
- `backend/core/apps/auth/models.py:18` defines the custom `User` (email login, MFA flags, password rotation metadata) and `backend/core/apps/auth/managers.py:14` supplies the email-first creator used by registration.
- `backend/core/apps/auth/api/serializers.py:1` also ships `UserSerializer`, embedding profile info and groups to give clients session context immediately after login/register.
- CSRF handshakes use `CSRFTokenView` (`backend/core/apps/auth/api/views.py:804`) decorated with `ensure_csrf_cookie`, letting the frontend fetch a token explicitly when bootstrapping forms.

## End-to-End Sequences

### Login (no MFA)
1. User submits the form on `frontend/src/app/login/page.jsx:115`; client-side validation (Yup) ensures the payload is well-formed.
2. RTK Query posts to `/api/auth/login/` with cookies and CSRF headers via the shared `baseQuery` (`frontend/src/store/api/authApi.js:7`).
3. `LoginView.post` validates credentials (`backend/core/apps/auth/api/views.py:39`) and calls `_complete_login` (`backend/core/apps/auth/api/views.py:98`).
4. `_complete_login` issues tokens, serializes the user, and plants the `refresh_token` cookie before returning `AuthAPIResponse.login_success` (`backend/core/utils/responses.py:293`).
5. The RTK mutation handler extracts `data.user` and `data.access_token` (`frontend/src/store/api/authApi.js:134`), stores them in Redux, and the component redirects the user after showing a toast (`frontend/src/app/login/page.jsx:123`).

### Login (with MFA)
1. Steps 1–2 mirror the standard login, but because `user.mfa_enrolled` is true, `LoginView.post` returns `AuthAPIResponse.mfa_required` with a short-lived JWT (`backend/core/apps/auth/api/views.py:47`).
2. The login page sees the `mfa_required` flag (`frontend/src/app/login/page.jsx:119`) and renders the MFA form while caching the `mfa_token` for the next request.
3. Submitting the MFA code hits `/api/auth/mfa/verify/` (`frontend/src/app/login/page.jsx:135`); `MFAVerifyView.post` decodes the token, verifies TOTP devices (`backend/core/apps/auth/api/views.py:182`), and, on success, reruns `_complete_login` so the final response matches the non-MFA case.
4. Redux receives the usual user/tokens payload, and the UI completes login with the same redirect logic.

### Registration
1. The registration page validates all fields with Yup (`frontend/src/app/register/page.jsx:19`) and posts to `register/` via `useRegisterMutation` (`frontend/src/app/register/page.jsx:83`).
2. `UserRegistrationSerializer` enforces unique email and password integrity (`backend/core/apps/auth/api/serializers.py:150`) before `User.objects.create_user` hashes and saves the account (`backend/core/apps/auth/api/serializers.py:174`).
3. `UserRegistrationView.post` issues tokens and sends `AuthAPIResponse.login_success` with HTTP 201 plus a refresh cookie (`backend/core/apps/auth/api/views.py:678`).
4. The mutation handler stores the credentials in Redux (`frontend/src/store/api/authApi.js:167`), and the page routes the new user into onboarding (`frontend/src/app/register/page.jsx:94`).

## Notes & Observations
- The access token only lives in Redux memory, while the refresh token is constrained to httpOnly cookies; this split aligns with the security posture configured in `SIMPLE_JWT` (`backend/core/core/settings.py:174`) and the base query’s `credentials: 'include'` setting.
- `remember_me` survives the full round-trip: it is captured on the form (`frontend/src/app/login/page.jsx:59`), validated (`backend/core/apps/auth/api/serializers.py:111`), encoded into the MFA token when needed (`backend/core/apps/auth/api/views.py:53`), and stretches the refresh expiry when login completes (`backend/core/apps/auth/api/views.py:102`).
- Because the backend wraps data under `data`, the login page should reference `result.data.mfa_required`; `result.mfa_required` (`frontend/src/app/login/page.jsx:119`) will only work if RTK Query ever flattens the envelope, so this is worth double-checking during testing.
- `log_auth_event` is currently a stub (`backend/core/apps/auth/utils/utils.py:6`), so audit logging hooks exist but do not yet persist to the database; toggling them later will not alter the response contracts described above.
- CSRF bootstrapping is explicit: clients can hit `/api/auth/csrf-token/` before the first mutating call, and every mutation reuses the cookie via `getCSRFToken`, matching Django’s expectation for cookie-based CSRF enforcement.
