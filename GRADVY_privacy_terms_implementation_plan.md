# Gradvy Privacy Policy & Terms Implementation Plan

This plan translates current code, docs, and UX into a complete, auditable Privacy & Terms system covering consent, cookies, data rights, policies, and compliance operations.

## Goals
- Publish clear Privacy Policy, Terms of Service, and Cookie Policy pages with versioning and audit trails.
- Enforce consent and policy acceptance, with graceful fallbacks and renewals.
- Provide GDPR/CCPA-style data subject rights (access/export, rectification, deletion, restriction, objection, portability).
- Ensure cookie and analytics usage aligns with user preferences and legal standards.
- Maintain logs, retention, and compliance automation.

## Current Inventory (Code & Docs)
- Cookies & Consent (Frontend)
  - `frontend/src/lib/cookieUtils.js`: cookie names, default preferences, consent state, CSRF extraction, cleaning unallowed cookies, banner controller.
  - `frontend/src/components/cookies/CookieConsentBanner.jsx`: banner with accept all/essential/customize + links to policies.
  - `frontend/src/components/cookies/CookiePreferencesModal.jsx`: granular controls; uses `COOKIE_POLICY_DATA` for display.
  - `frontend/src/components/cookies/CookieManager.jsx`: initializes banner + modal.
- Privacy UI (Frontend)
  - `frontend/src/components/privacy/ConsentManagement.jsx`: GDPR consent UI for categories and history; calls endpoints under `/api/preferences/consent/...` (not all exist yet), and uses localStorage token.
  - `frontend/src/components/settings/PrivacySettings.jsx`: local-only toggles (no API integration yet).
  - Footer links: `Privacy Policy` → `/privacy`, `Terms of Service` → `/terms`, `Cookie Policy` → `/cookies` (pages not all present; cookie policy path mismatch).
- Pages present
  - `frontend/src/app/cookie-policy/page.jsx`: Cookie Policy page exists.
  - `frontend/src/app/settings/privacy/page.jsx`: privacy settings page exists.
  - Missing: `/privacy` or `/privacy-policy` page; `/terms` page.
- Backend Privacy/Consent
  - Middleware: `SecurityHeadersMiddleware`, `CookieSecurityMiddleware`, `CookieConsentMiddleware` (`backend/core/core/middleware.py`).
  - Models: `PrivacySettings`, `ConsentRecord`, fields for versions and consent (`backend/core/apps/preferences/models.py`).
  - Views: `PrivacyConsentAPIView` (record/retrieve privacy settings), analytics endpoints check consent (`backend/core/apps/preferences/views.py`). Some privacy helpers exist but are not routed.
  - Tasks: `privacy_compliance_audit` and consent-aware processing in `backend/core/apps/preferences/tasks.py`.
- Docs
  - `COOKIE_IMPLEMENTATION_GUIDE.md`, `PREFERENCES_SYSTEM_SUMMARY.md`, `DATA_PIPELINE_GUIDE.md`, `SOCIAL_AUTH_GUIDE.md` mention privacy/consent and audits.

## Gaps & Risks
- Frontend ConsentManagement endpoint mismatch: expects `/api/preferences/consent/{id}/`, `/consent/revoke-all/`, `/consent-history/download/`. Backend exposes only `PrivacyConsentAPIView` (`GET/POST`), plus helper methods not routed.
- Footer links mismatch: `/privacy`, `/terms`, `/cookies` vs existing `/cookie-policy` only.
- LocalStorage token usage in `ConsentManagement.jsx` conflicts with RTK Query + httpOnly cookie token flow.
- No public policy pages for Privacy/Terms; no acceptance UI/flow implemented.
- DSR endpoints (export/delete/rectify/restrict) not exposed.
- PDF export of consent history not implemented (component expects it).

## Policy Documents (Pages & Content)
- Create public pages with clear routes:
  - `frontend/src/app/privacy-policy/page.jsx`
  - `frontend/src/app/terms/page.jsx`
  - Normalize cookie policy path: add alias page `frontend/src/app/cookies/page.jsx` that redirects to `/cookie-policy` or duplicate content.
- Content structure (high-level):
  - Privacy Policy: controller identity, data collected, purposes/legal bases, cookies and tracking, data sharing, retention, rights (GDPR/CCPA), international transfers, security, children’s privacy, contact/DPO, changes and versioning.
  - Terms: definitions, eligibility, service use, user content and license, acceptable use, payments/refunds (future), IP, disclaimers/limitation of liability, termination, governing law, dispute resolution, changes/versioning, contact.
  - Cookie Policy: categories, purposes, duration, 3rd parties, how to change settings; align with `COOKIE_POLICY_DATA`.
- Versioning & change logs: include current version and last updated date top-of-page; maintain versions in repo.

## Policy Versioning & Acceptance Tracking
- Data model already includes: `privacy_policy_version`, `terms_accepted_version`, `gdpr_consent_date` in `PrivacySettings`.
- Implement flows:
  - On signup or before critical features: require Terms acceptance and Privacy Policy acknowledgement.
  - On version bump (server-configured): block until re-accepted (soft-block with read-only mode for non-essential areas if desired).
- Backend endpoints:
  - `GET /api/privacy/versions/` → { privacy_policy_version, terms_version, cookie_policy_version, last_updated }
  - `POST /api/privacy/accept/` → body { policy: 'privacy'|'terms'|'cookie', version, consent_types? } → records acceptance in `PrivacySettings` (with IP + UA), updates fields and timestamps.
- Frontend UI:
  - Interstitial modal after login prompting acceptance if versions mismatch.
  - Persist acceptance state to avoid repeat prompts.

## Consent & Cookie Management
- Keep cookie consent UI; ensure FE stores consent with `cookieUtils` and hides non-essential trackers.
- Align backend consent endpoints for FE:
  - `GET /api/preferences/consent/` → summary and `consent_records` (from `get_privacy_summary()` + history).
  - `PUT /api/preferences/consent/{consent_id}/` → update specific consent record (grant/withdraw, expire update) and append to `consent_history`.
  - `POST /api/preferences/consent/revoke-all/` → withdraw all non-essential consents and enforce minimal collection.
  - `GET /api/preferences/consent-history/download/` → return JSON or generate PDF (defer PDF or use simple HTML-to-PDF).
- Replace localStorage auth in `ConsentManagement.jsx` with RTK Query base (`credentials: 'include'` + `Authorization` from Redux) to align with `apiSlice`.
- Link cookie banner to policy pages; ensure `CookieConsentMiddleware` drives first-visit banner.

## Data Subject Rights (DSR) Endpoints
- Export (access/portability):
  - `POST /api/privacy/data-export/` → enqueue Celery job to package user data (Postgres auth profile + Mongo preferences/interactions/recs/consent history) as JSON/ZIP; email link or return signed URL.
  - `GET /api/privacy/data-export/{job_id}/` → status + download when ready.
- Erasure (Right to be Forgotten):
  - `POST /api/privacy/request-erasure/` → schedule deletion/anonymization; immediate deactivation; cascade removal across Mongo collections; scrub PII in Postgres.
- Rectification & Restriction:
  - `POST /api/privacy/rectify/` → allow correcting profile fields.
  - `POST /api/privacy/restrict/` → toggle reduced processing (sets privacy level minimal, pauses analytics/behavioral processing, clears non-essential caches).
- Objection:
  - `POST /api/privacy/object/` → record and enforce opt-out for marketing/profiling.
- Audit trail: store DSR requests with timestamps and outcomes.

## Retention & Deletion
- Use existing `PrivacySettings.data_retention_months`, auto-delete settings, and `cleanup_expired_data()` in models.
- Apply TTL indexes for ephemeral data (analytics events, training data) based on privacy level.
- Implement periodic Celery tasks to:
  - Purge events beyond retention windows.
  - Anonymize rather than delete where required (replace identifiers with hashes).

## Third Parties & Transfers
- Maintain registry of 3rd-party processors/services in config (e.g., GA, Sentry, Mailchimp, Ads).
- Surface in Privacy & Cookie policies; allow toggling per consent category.
- For cross-border transfers, include SCCs notice in policy; no runtime changes needed.

## Logging & Audits
- Record policy acceptance with IP/UA and versions; store consent changes in `consent_history`.
- Daily `privacy_compliance_audit` runs via Celery Beat to: check missing consents, revoke processing for non-consenting users, enforce retention, and report metrics.
- Expose `GET /api/privacy/audit-summary/` for internal admin (counts, violations, actions taken).

## Backend Changes (Summary)
- Routes (extend `apps.preferences.urls`):
  - `privacy/consent/` (GET)
  - `privacy/consent/{id}/` (PUT)
  - `privacy/consent/revoke-all/` (POST)
  - `privacy/consent-history/download/` (GET)
  - `privacy/versions/` (GET)
  - `privacy/accept/` (POST)
  - `privacy/overview/`, `privacy/quick-toggle/` (optional: expose existing helpers)
  - `privacy/data-export/` (POST, GET status)
  - `privacy/request-erasure/` (POST)
  - `privacy/rectify/` (POST), `privacy/restrict/` (POST), `privacy/object/` (POST)
- Views: build on `PrivacyConsentAPIView` and existing helpers in `views.py` and `tasks.py`.
- Serializers: add serializer for consent updates and acceptance records.

## Frontend Changes (Summary)
- Pages:
  - Add `/privacy-policy`, `/terms` pages; alias `/cookies` → `/cookie-policy`.
  - Update Footer links to existing routes.
- Consent Management:
  - Switch to RTK Query endpoints tied to new backend routes; remove localStorage token usage.
  - Add “Download consent history” using JSON first; PDF later.
- Policy Acceptance Flow:
  - After login, check `/api/privacy/versions/` vs user’s stored versions; show modal to accept.
  - Record via `/api/privacy/accept/`.
- Settings:
  - Bind `PrivacySettings.jsx` toggles to API (`privacy_quick_toggle` or new routes).

## Phased Plan & Deliverables
- Phase 0: Routing & UX (1 week)
  - Add Privacy/Terms pages; correct Footer links; add `/cookies` alias.
  - Wire cookie banner links.
- Phase 1: Consent API Alignment (1–2 weeks)
  - Implement consent routes to match `ConsentManagement.jsx` needs or update component to new contract.
  - Replace localStorage auth in consent UI with RTK Query (cookies + CSRF).
- Phase 2: Policy Versioning & Acceptance (1 week)
  - Add `privacy/versions` + `privacy/accept` endpoints.
  - Add acceptance modal post-login; update `PrivacySettings` fields.
- Phase 3: DSR Endpoints (2 weeks)
  - Implement data export, erasure, rectification, restriction, objection endpoints + Celery jobs.
  - Add admin-only audit summary endpoint.
- Phase 4: Retention & Audits (1 week)
  - TTL indexes, purge tasks; integrate `privacy_compliance_audit` scheduling.
- Phase 5: Documentation & Compliance (ongoing)
  - Publish policies with version stamps; update `COOKIE_IMPLEMENTATION_GUIDE.md` with links.
  - Add internal runbooks for DSR handling.

## Acceptance Criteria & Checklists
- Legal Pages
  - Published at `/privacy-policy`, `/terms`, `/cookie-policy` (and `/cookies` alias).
  - Version and last-updated visible; links appear in footer and banner/modal.
- Consent & Cookies
  - Banner appears for new visitors; preferences persist; non-essential cookies removed when disabled.
  - Consent categories map to backend `PrivacySettings` flags and `consent_history` records.
- Policy Acceptance
  - On version bump, users are prompted and must accept; acceptance recorded with IP/UA and timestamp.
- DSR
  - Users can request export (job created and downloadable), deletion (scheduled and confirmed), rectification, restriction, objection; actions logged.
- Security & Compliance
  - CSRF present; httpOnly refresh cookies used; no tokens in localStorage.
  - Retention enforced via TTL; audit reports available.

## Quick Wins (Do Now)
- Add Privacy & Terms pages and fix footer links.
- Align ConsentManagement endpoints or component to backend contract; remove localStorage token use.
- Expose `/api/preferences/privacy/consent/` (GET/PUT/revoke-all) and `/privacy/versions` + `/privacy/accept`.

## Notes
- Keep privacy endpoints under `apps.preferences` for now to avoid app proliferation; consider `apps.privacy` if scope grows.
- PDF generation for consent history can be deferred; start with JSON/CSV.
- Internationalization: plan for locale-specific policy pages later.

