# Gradvy Data Architecture & UX Implementation Plan

Scope: Operationalize data storage/architecture and UX best practices from GRADVY_DATA_COLLECTION_AND_MANAGEMENT_PLAN.md and align with GRADVY_plan.md, grounded in the current codebase.

## Summary
- Polyglot persistence is in place (Postgres + Redis + Mongo). Use Mongo for flexible user personalization data and cached recommendations; Postgres for accounts/auth; Redis for caching/broker. Precompute recommendations and analytics; serve from cache for low latency. Start without Kafka/warehouse; add streaming/warehouse when data volume and ML maturity require it.
- UX emphasizes consent, transparency, progressive profiling, and performance. Provide user controls (opt-out, edits), and fallbacks for cold start. Optimize latency with precomputation and caching.

## Current State (Codebase)
- Backend
  - Django 5.1, JWT + MFA, Celery, Redis, Postgres, MongoEngine for Mongo.
  - Mongo models for personalization: user preferences, interactions, learning sessions, cached recommendations, AI training data.
  - REST API: preferences CRUD, onboarding/quick-onboarding, interactions logging, analytics, and recommendation retrieval (with mock generation).
  - Infra: Docker Compose for Postgres, Redis, Mongo; Mongo init + sample data scripts.
- Frontend
  - Next.js + Tailwind + RTK Query for preferences API; onboarding and preferences dashboards present; cookie consent UI. RecommendationSettings uses raw fetch + localStorage (inconsistent with RTK Query + cookie-based auth).
- Docs
  - Plans and guides present (cookie/security, preferences summary, project plans).

## Inconsistencies & Gaps
- Endpoint mismatch
  - FE uses `/api/preferences/recommendations/generate/` and `/api/preferences/recommendations/feedback/`.
  - BE exposes `GET/POST /api/preferences/recommendations/` only.
- Token handling
  - RecommendationSettings fetches with `localStorage.getItem('accessToken')`; the app uses RTK Query + httpOnly cookie refresh.
- Duplicate UI component filenames differing by case (`Button.jsx/button.jsx`, `Card.jsx/card.jsx`) risk platform issues.
- Test portability
  - `backend/test_preferences_flow.py` uses absolute local paths.
- Missing features
  - No course aggregation services; no real recommendation algorithm; no event streaming/warehouse.

## Architecture Decisions (Data Storage & Processing)
- Operational stores
  - Postgres: auth, admin, transactional entities (Django ORM).
  - MongoDB: denormalized, evolving personalization data (user profiles, interactions), learning sessions, cached recommendations, AI training data.
  - Redis: cache + Celery broker.
- Processing pattern
  - Ingest interactions via REST; batch/periodic aggregation with Celery; precompute recommendations and analytics into Mongo.
  - Serve reads from Mongo cache layers; keep responses <200ms on cache hit, <1.2s on miss (SLI).
- Indexing & TTL
  - Ensure indexes on: `user_preferences.user_id`, `user_preferences.updated_at`, `user_preferences.basic_info.learning_goals`, `user_preferences.interactions.timestamp`; `course_recommendations.user_id`, `course_recommendations.expires_at`.
  - Add TTL for ephemeral events (e.g., training data older than N days) when appropriate.
- Event streaming (later)
  - Add Kafka/Kinesis + warehouse (ClickHouse/BigQuery/etc.) only after MVP to support offline training and heavy analytics.

## UX & Best Practices
- Consent & transparency: cookie banner present; add “Personalization” toggle, reasons-why for recommendations, and data export/delete.
- User control: editable preferences; “not interested” per recommendation feeds AI training data.
- Progressive profiling: minimal onboarding; contextual prompts later to enrich profile.
- Performance: async logging, batching on FE, precompute recommendations, cache results.
- Cold start: show popular/trending by goal/platform; progressively personalize with first interactions.
- Security: httpOnly refresh, no tokens in localStorage, encryption for sensitive fields, role-restricted exports.
- Ethical use: optimize for learning outcomes (completion/skill progress), not vanity engagement.

## Phase-Wise Implementation

### Phase 0: Align & Stabilize (1–2 weeks)
- Endpoints: Align FE with BE for recommendations.
  - Option A: Update FE to use `GET/POST /api/preferences/recommendations/` via RTK Query.
  - Option B: Add BE routes `/api/preferences/recommendations/generate/` and `/feedback/` to match current FE component.
- Token flow: Remove localStorage usage in `RecommendationSettings`; use RTK Query base (cookie-based refresh, CSRF).
- UI duplicates: Remove case-duplicate UI components and fix imports.
- Housekeeping: Remove/repurpose `backend/core/settings/base.py`; fix absolute paths in tests.

Deliverables
- Updated FE to use RTK Query for recs; consistent auth handling.
- Endpoint parity confirmed and documented.
- Duplicate UI files removed; CI/check added for case conflicts (optional).

### Phase 1: Data Collection & Instrumentation (1–2 weeks)
- Event schema: Document standard interaction types/fields/contexts.
- FE logging: Centralize interaction logging with `logUserInteraction` on key actions; auto page_view on route change.
- BE ingestion: Validate/normalize events, apply DRF throttling; consider bulk insert endpoint.

Deliverables
- Event schema doc + validation; robust ingestion endpoint; FE hooked for key events.

### Phase 2: Storage & Schema Hardening (1–2 weeks)
- Indexes/TTL: Verify/create required indexes; add TTL for ephemeral logs where applicable.
- Schema evolution: Ensure safe upserts for profile updates; finalize `learning_sessions` usage.
- Encryption: Encrypt sensitive fields at rest as needed; scrub PII from logs.

Deliverables
- Index/TTL plan executed; migration scripts; encryption guidelines.

### Phase 3: Recommendation Pipeline v1 (2–3 weeks)
- Generator: Implement heuristic/rule-based rec generator (learning goals, prefs, difficulty, recent interactions).
- Celery task: Periodic regeneration and on-demand trigger; respect expiration policy.
- Feedback: Add `/feedback/` endpoint to log rec feedback to `ai_training_data`.
- API: Optional params to guide generation (limit, diversity, free, ratings); return rationale per item.

Deliverables
- Celery task + API; cached recommendations persisted; feedback loop operational; tests/fixtures for recs.

### Phase 4: Analytics & Insights v1 (1–2 weeks)
- Aggregations: Periodic jobs to compute top interests, completion rates, preferred times; store in `ai_insights`.
- API/UI: Extend analytics endpoint; render actionable insights on dashboard.

Deliverables
- Materialized insights; analytics API v1; UI widgets.

### Phase 5: UX Controls & Transparency (1–2 weeks)
- Personalization toggle: Opt-out path and graceful fallback to non-personalized content.
- Data rights: Export (JSON) and delete endpoints; surface a readable “What we use” summary.
- Progressive prompts: Timely, unobtrusive prompts to fill key missing preferences.

Deliverables
- Settings controls live; export/delete APIs; copy/UX for transparency.

### Phase 6: Performance & Scalability (2 weeks)
- Caching: Redis caching for per-user recs/analytics snapshots; cache invalidation on updates.
- Back-pressure: DRF throttling/batching; Celery queues & concurrency tuned; idempotent tasks.
- Observability: Logs/metrics for latency, cache hit ratio, rec freshness; error budgets.

Deliverables
- Perf dashboards; SLO adherence; improved cache hit rate and rec freshness.

### Phase 7: Advanced Personalization (3–6 weeks, post-MVP)
- Course aggregation: Microservice to ingest/normalize courses from Udemy/Coursera/YouTube.
- Reranking: Add collaborative filtering/item-item similarity; later embeddings + vector search.
- Streaming/warehouse: Kafka/Kinesis + ClickHouse/BigQuery for training/offline analytics when warranted.

Deliverables
- Catalog service + schema; baseline CF/rerank; roadmap for embedding-based search and ML pipeline.

## API Contract Adjustments (Recommendations)
- `GET /api/preferences/recommendations/?limit=10&diversity=0.6&include_free=true&consider_ratings=true`
  - Returns cached or triggers async refresh; includes `source: cached|generated` and `algorithm_version`.
- `POST /api/preferences/recommendations/`
  - Body: optional generation hints (same params as above). Forces regeneration; returns newly cached rec set.
- `POST /api/preferences/recommendations/feedback/`
  - Body: `{ recommendation_id|course_id, feedback: 'thumbs_up'|'thumbs_down'|'dismissed', reason?: string }` -> logs to `ai_training_data`.

## Data Retention & Indexing
- Retain raw interactions for 90–180 days (configurable), aggregate into insights; purge older events (TTL).
- Ensure compound indexes for common filters (`user_id` + time, `user_id` + expiration).

## Observability & SLIs
- Rec latency: P95 < 200ms (cache hit), < 1.2s (miss + generation path async).
- Cache hit ratio: > 80% for dashboard loads.
- Rec freshness: < 24h default; < 2h for highly active users.
- Error rate: < 0.5% 5xx on personalization endpoints.

## Immediate Quick Wins
- Align FE recs to RTK Query + cookie auth; remove localStorage token usage in recommendation flows.
- Unify endpoints (choose Option A or B) and document.
- Remove duplicate UI components by case to prevent cross-platform issues.
- Fix test script path portability.

## Risks & Mitigations
- Data growth in Mongo: Apply TTL, archive strategy, and periodic compaction; move heavy analytics to warehouse when needed.
- Latency spikes: Precompute + Redis cache; rate limit generation; monitor and auto-scale Celery workers.
- Privacy concerns: Clear consent/opt-out; data minimization; encrypt sensitive fields; audit logs.

