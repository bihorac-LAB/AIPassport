# AIPassport Architecture

Production architecture for the React + FastAPI rebuild. See `docs/legacy-audit.md` for what the
Streamlit implementation did and why the content was reorganized.

---

## 1. Topology

```
 Browser  ──or──  Canvas iframe (?embed=1)
    │
    ▼
 Netlify  (static SPA, frontend/dist)
    │  HTTPS + credentialed fetch (refresh cookie)
    ▼
 Caddy / Nginx on EC2  :443  api.<domain>
    │  reverse proxy, HSTS, request size cap
    ▼
 Uvicorn / FastAPI     127.0.0.1:8000   (systemd unit, never public)
    │  asyncpg pool
    ▼
 PostgreSQL 16         127.0.0.1:5432   (localhost only, no public SG rule)
    │
    └── outbound HTTPS → LLM provider (NaviGator / Gemini)
```

The browser never holds a database credential, an LLM key, or a JWT signing secret. The only secret
that reaches the client is a short-lived access token held **in memory**, plus an `HttpOnly` refresh
cookie the JavaScript cannot read.

---

## 2. Repository layout

```
/
├── frontend/                     React + TypeScript + Vite SPA  → Netlify
│   ├── src/
│   │   ├── api/                  typed API client, TanStack Query hooks
│   │   ├── auth/                 AuthProvider, route guards, token refresh
│   │   ├── analytics/            trackEvent(), batching queue, debounce helpers
│   │   ├── components/           design-system primitives + shared learning UI
│   │   ├── content/              typed educational content (modules, pages, questions)
│   │   ├── activities/           interactive learning components
│   │   ├── pages/                route-level screens
│   │   └── styles/               design tokens + global CSS
│   ├── e2e/                      Playwright specs
│   ├── netlify.toml
│   └── .env.example
│
├── backend/                      FastAPI + SQLAlchemy 2.x + Alembic  → EC2
│   ├── app/
│   │   ├── api/v1/               routers (auth, users, modules, progress, responses, events, ai, admin)
│   │   ├── auth/                 password hashing, JWT, dependencies, rate limiting
│   │   ├── models/               SQLAlchemy ORM
│   │   ├── schemas/              Pydantic request/response models
│   │   ├── services/             business logic (progress, responses, events, llm)
│   │   ├── repositories/         data access
│   │   ├── core/                 settings, logging, security, errors
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── content/                  authoritative content manifest (seed source)
│   └── .env.example
│
├── legacy/                       preserved Streamlit implementation
├── deploy/                       systemd unit, Caddyfile, nginx.conf
└── docs/                         legacy-audit.md, architecture.md, deployment.md
```

---

## 3. Frontend architecture

### 3.1 Stack decisions

| Choice | Rationale |
| --- | --- |
| Vite + React 19 + TypeScript strict | Fast builds, first-class Netlify support, no framework server needed. |
| React Router (data-router, `createBrowserRouter`) | Route-level code splitting via `lazy()`; every module page is its own chunk. |
| TanStack Query | Server state, caching, retries, and mutation lifecycle for autosave. |
| Custom design system (~700 lines of CSS + primitives) | The UI surface is small and specific (cards, sliders, question blocks, charts). A component library would add >200KB for widgets we then have to restyle anyway. Radix-style a11y patterns are implemented directly on native elements, which are keyboard- and screen-reader-correct by default. |
| `zustand` for the small amount of client state | Track preference, AI panel open/closed, embed mode. ~1KB, no provider tree. |
| Hand-written SVG charts | Charts are simple (line, bar, scatter, heatmap, histogram) and must be theme-aware, responsive, and accessible with a data-table fallback. Avoids ~150KB of charting library. |

No dependency on Plotly, D3, matplotlib, scikit-learn, or SHAP: every simulation is a deterministic
closed-form computation implemented in `src/activities/lib/`, so slider interactions are instant and
require no network round-trip.

### 3.2 Content system

Educational copy is **never** embedded in component JSX. Content lives in
`frontend/src/content/` as typed structures:

```ts
type ModulePage = {
  id: string;                    // "m1p1" — stable, used by API + analytics
  slug: string;                  // "demystifying-ai"
  title: string;
  kicker: string;
  objectives: string[];
  sections: Section[];
  contentVersion: number;        // bumped when wording changes materially
};

type Section =
  | { kind: 'prose'; id: string; heading?: string; body: string[] }
  | { kind: 'callout'; id: string; tone: Tone; heading: string; body: string[] }
  | { kind: 'reveal'; id: string; label: string; body: string[] }   // progressive disclosure
  | { kind: 'question'; id: string; question: Question }
  | { kind: 'activity'; id: string; activity: ActivityKey; heading: string; intro?: string }
  | { kind: 'aiActivity'; id: string; prompt: AiPromptKey; heading: string; ... };
```

Questions carry stable IDs and their own version:

```ts
type Question = {
  id: string;              // "m1p1.q2" — never reused, never renumbered
  version: number;
  type: 'single_choice' | 'multi_choice' | 'free_text' | 'numeric' | 'likert' | 'slider_estimate' | 'structured';
  prompt: string;
  options?: Option[];      // each with its own stable value + per-option feedback
  correct?: string | string[] | { min: number; max: number };
  explanation?: string;
};
```

`ActivityKey` maps to a lazily-imported React component in `src/activities/registry.ts`. Rewording a
question or paragraph is a content-file edit; historical responses stay interpretable because the
version is recorded on every stored response.

The same content manifest is exported to JSON and consumed by the backend seeder (§7.3), so the
database's `modules` / `module_pages` / `questions` rows and the client always agree.

### 3.3 Rendering and layout

- `AppShell` renders global chrome. In embed mode (`?embed=1`, or `window.self !== window.top`)
  the header/footer/global nav collapse to a single compact context bar; the learning content and the
  AI panel remain.
- No `100vh`. Layout uses intrinsic content height plus `min-height: 100%` so a Canvas iframe of any
  height works. The AI tutor is a right-side drawer at ≥1100px and a bottom sheet below that.
- Breakpoints: 560 / 760 / 1100 / 1440. Page content max-width 68ch for prose, full width for activities.
- `prefers-reduced-motion` disables all transitions; `prefers-color-scheme` plus a `data-theme`
  override drive light/dark.

### 3.4 Autosave and error handling

Every question and activity result goes through `useAutosaveResponse`:

1. Local state updates immediately (learner never waits).
2. Change is debounced (600ms for text/slider, immediate for discrete choices).
3. `POST /api/v1/responses` with an `idempotency_key` = `sha256(questionId|attempt|payloadHash)`.
4. UI shows `Saving…` → `Saved` → `Saved (offline copy kept)` on failure.
5. Failures retry with exponential backoff; the payload is mirrored to `localStorage` under a
   non-sensitive key so a reload does not lose work, and is replayed on next successful auth.

### 3.5 Analytics service

`src/analytics/track.ts` exposes:

```ts
trackEvent(type: EventType, ctx?: EventContext, meta?: Json): void   // queued
trackImmediate(type, ctx, meta): Promise<void>                        // for session_ended
useInteractionTracker(activityId)                                     // returns start/change/complete
```

Behavior:

- Events are queued and flushed to `POST /api/v1/events` in batches (max 25 events / 5s / on
  `visibilitychange` hidden / on `pagehide` via `sendBeacon`-style keepalive fetch).
- High-frequency interactions never emit per-tick events. `useInteractionTracker` emits
  `parameter_changed` at most once per 1500ms trailing-debounce, plus a single
  `activity_completed` carrying the final parameter set and the interaction count.
- A client-side allowlist of event types prevents accidental telemetry sprawl; the backend enforces
  the same allowlist.

---

## 4. Backend architecture

### 4.1 Layering

```
api/v1/<router>.py     HTTP concerns only: auth dependency, validation, status codes
   └── services/       business rules, transactions, invariants
          └── repositories/   SQLAlchemy queries
                 └── models/  ORM
schemas/               Pydantic v2 in/out models; ORM objects never leave the service layer
core/                  settings, logging, security primitives, exception handlers
```

`app.state` holds the async engine and sessionmaker. Every request gets an `AsyncSession` via
dependency injection, committed by the service layer, rolled back by the exception handler.

### 4.2 Configuration

`app/core/config.py` is a `pydantic_settings.BaseSettings`. Every deployment-specific value is an
environment variable with a development default that is *safe* but not *production-viable*
(`ENVIRONMENT=production` refuses to boot with a default `SECRET_KEY` or a wildcard CORS origin).

### 4.3 Errors and logging

- A single `APIError` hierarchy → RFC-7807-ish JSON `{detail, code}`; never a stack trace.
- `structlog` JSON logs with a per-request `request_id` (propagated to the response header).
- Request/response middleware logs method, path, status, duration_ms, user_id (UUID only).
- A redaction processor strips `password`, `token`, `authorization`, `cookie`, `api_key` keys.
- Logged auth failures record the email **hash prefix**, never the address.

### 4.4 Rate limiting

In-process token buckets keyed by `(scope, identity)` where identity is user UUID when
authenticated and client IP otherwise. Applied to: login (10/15min/IP + 5/15min/email),
register (5/hour/IP), password reset request (3/hour/email), AI chat (20/hour/user, 200/day/user),
events (600/min/user), responses (300/min/user). A `Retry-After` header accompanies every 429.
For multi-instance deployments the limiter is a single class with one method to swap for Redis.

---

## 5. Identity and authentication

### 5.1 Data model (LTI-ready from day one)

```
users                              user_identities
─────                              ───────────────
id            uuid PK   ◄────────  user_id       uuid FK
email         citext U             provider      enum(local, canvas_lti, uf_sso)
display_name                       provider_subject  text
role          enum                 UNIQUE (provider, provider_subject)
track_pref                         password_hash  text NULL   -- local only
is_active                          email_verified bool
created_at                         last_login_at
```

`users.id` is the canonical identifier used by **every** other table. Credentials live on
`user_identities`, not on `users`. Adding Canvas is then purely additive: validate the LTI 1.3
launch, upsert `user_identities(provider='canvas_lti', provider_subject=<iss|sub>)`, link it to an
existing `users` row (matched by verified email, or create one), and mint the same session. No
existing table changes; no frontend change beyond a new launch route.

### 5.2 Token strategy

| Token | Lifetime | Storage | Contents |
| --- | --- | --- | --- |
| Access | 15 min (`ACCESS_TOKEN_EXPIRE_MINUTES`) | **JS memory only** | `sub`=user uuid, `sid`=auth session uuid, `role`, `jti`, `exp` |
| Refresh | 30 days (`REFRESH_TOKEN_EXPIRE_DAYS`) | `HttpOnly; Secure; SameSite=None; Path=/api/v1/auth` cookie | opaque 256-bit random, stored **hashed** in `auth_sessions` |

- `SameSite=None` is required for the Netlify-origin → EC2-API cross-site call and for Canvas iframes;
  it is paired with `Secure`, a strict CORS allowlist, and a double-submit CSRF token so a third-party
  page cannot silently drive the refresh endpoint.
- Refresh is **rotating with reuse detection**: each refresh issues a new opaque token and marks the
  old one `rotated_to`. Presenting an already-rotated token revokes the entire session family and
  logs a `security.refresh_reuse` event.
- `POST /auth/logout` revokes the current auth session; `POST /auth/logout-all` revokes all of a
  user's sessions.
- Passwords are hashed with **Argon2id** (`argon2-cffi`, t=3, m=64MiB, p=4). Plaintext is never
  logged, never stored, and never returned.
- Password reset uses a single-use, 1-hour, hashed token; the response is identical whether or not
  the email exists (no account enumeration). SMTP is optional in development — the token is written
  to the log at DEBUG so the flow is testable without a mail server.

### 5.3 Authorization

`get_current_user` (required) and `get_optional_user` dependencies decode the access token, verify
the auth session is still active, and load the user. `require_role('instructor'|'admin')` guards
admin/analytics routes. **Every** write derives `user_id` from the token; no endpoint accepts a
`user_id` in its body — the Pydantic schemas do not define the field, so a client that sends one
gets a 422 under `model_config = ConfigDict(extra='forbid')`.

---

## 6. Database model

```
users ──1:N── user_identities
  │
  ├──1:N── auth_sessions          (refresh-token family, revocation, UA/IP hash)
  ├──1:N── learning_sessions      (pedagogical visit: started_at, last_seen_at, ended_at, embed?)
  ├──1:N── page_progress          (user × module_page: state, seconds, section cursor)
  ├──1:N── question_responses     (append-only attempts)
  ├──1:N── events                 (analytics stream)
  ├──1:N── ai_conversations ──1:N── ai_messages
  └──1:N── password_reset_tokens

modules ──1:N── module_pages ──1:N── questions
```

### 6.1 Tables

| Table | Key columns | Notes |
| --- | --- | --- |
| `users` | `id uuid pk`, `email citext unique`, `display_name`, `role`, `track_pref`, `is_active`, timestamps | Only PII-bearing table. |
| `user_identities` | `id uuid`, `user_id`, `provider`, `provider_subject`, `password_hash`, `email_verified`, `last_login_at` | Unique `(provider, provider_subject)`; partial unique index guarantees at most one `local` identity per user. |
| `auth_sessions` | `id uuid`, `user_id`, `refresh_token_hash unique`, `rotated_to_id`, `revoked_at`, `expires_at`, `user_agent`, `ip_hash` | IP is stored as a salted hash, never raw. |
| `learning_sessions` | `id uuid`, `user_id`, `started_at`, `last_seen_at`, `ended_at`, `is_embedded`, `client_meta jsonb` | Separate from auth: a learner may have several study sittings under one login. |
| `modules` | `id uuid`, `key` ("module-1") unique, `position`, `title`, `subtitle`, `accent`, `content_version` | Seeded from the content manifest. |
| `module_pages` | `id uuid`, `module_id`, `key` ("m1p1") unique, `position`, `slug`, `title`, `kind`, `objectives jsonb`, `content_version` | Exactly 2 rows per module, enforced by a seeder assertion and a `unique(module_id, position)` with `position in (1,2)` check. |
| `questions` | `id uuid`, `page_id`, `key` ("m1p1.q2") unique, `position`, `type`, `prompt`, `spec jsonb`, `version`, `is_active` | `spec` holds options/correctness/scale; wording change ⇒ `version+1`. |
| `question_responses` | `id uuid`, `user_id`, `question_id`, `question_key`, `question_version`, `module_key`, `page_key`, `learning_session_id`, `attempt_no`, `answer jsonb`, `is_final`, `is_correct bool NULL`, `score numeric NULL`, `response_time_ms`, `client_submitted_at`, `created_at` (server, authoritative), `idempotency_key unique` | **Append-only.** A new submission for the same question creates `attempt_no+1`; nothing is overwritten. `is_final` marks the learner's latest. |
| `activity_results` | `id uuid`, `user_id`, `activity_key`, `module_key`, `page_key`, `learning_session_id`, `attempt_no`, `payload jsonb`, `created_at` | Structured outputs of simulators (e.g. model card, chosen parameters, prediction-vs-actual). |
| `page_progress` | `id uuid`, `user_id`, `page_id`, `module_key`, `page_key`, `status enum(not_started, in_progress, completed)`, `sections_completed jsonb`, `last_section_id`, `seconds_spent`, `visit_count`, `started_at`, `completed_at`, `updated_at`; `unique(user_id, page_id)` | The one intentionally-mutable learner table (it is a projection, not evidence). |
| `events` | `id uuid`, `user_id`, `learning_session_id`, `event_type`, `module_key`, `page_key`, `activity_key`, `question_key`, `metadata jsonb`, `client_ts`, `created_at` (server, authoritative) | Append-only. No email/name/Canvas ID ever written here. |
| `ai_conversations` / `ai_messages` | conversation scoped to `(user, page)`; messages store role, content, token counts, latency, model, `error_code` | Powers usage tracking and the "how often is the tutor used" research question. |
| `password_reset_tokens` | `id`, `user_id`, `token_hash unique`, `expires_at`, `used_at` | Single-use. |

### 6.2 Indexing

`events(user_id, created_at)`, `events(event_type, created_at)`, `events(module_key, page_key)`,
`question_responses(user_id, question_key, attempt_no)`,
`question_responses(question_key) where is_final`, `page_progress(user_id, status)`,
`learning_sessions(user_id, started_at desc)`, `auth_sessions(user_id) where revoked_at is null`.

### 6.3 PII separation

`users` is the only table with an email or a name. Every learning/telemetry table references
`user_id uuid` and nothing else — no denormalized email, no display name, no future Canvas ID. A
research export therefore only needs a per-study pseudonym mapping, and dropping the `users` row (or
replacing its email with a tombstone) de-identifies the entire learning history in one statement.

### 6.4 Migrations

Alembic from the first commit. `alembic/versions/0001_initial_schema.py` creates everything above
and is written to be **additive only**: it `CREATE`s and never `DROP`s pre-existing objects, and the
migration is guarded so an already-populated database is left untouched. `alembic upgrade head`
is the only supported way to change production schema.

---

## 7. API surface

All routes under `/api/v1`. OpenAPI at `/docs` (disabled when `ENVIRONMENT=production` unless
`ENABLE_DOCS=true`).

| Method & path | Purpose |
| --- | --- |
| `POST /auth/register` | create user + local identity, set refresh cookie, return access token |
| `POST /auth/login` | authenticate, rotate session |
| `POST /auth/refresh` | rotate refresh cookie, new access token (CSRF-protected) |
| `POST /auth/logout`, `/auth/logout-all` | revoke session(s) |
| `POST /auth/password-reset/request`, `/confirm` | reset flow |
| `POST /auth/verify-email/request`, `/confirm` | email verification |
| `GET  /users/me`, `PATCH /users/me` | profile + track preference |
| `GET  /modules` | module list with page stubs and the caller's progress summary |
| `GET  /modules/{module_key}` | module detail + both pages + progress |
| `GET  /modules/{module_key}/pages/{page_key}` | page metadata, questions, saved responses |
| `POST /progress/pages/{page_key}` | upsert progress (status, section cursor, seconds delta) |
| `GET  /progress/me` | full progress + resume pointer |
| `GET  /questions/{question_key}` | question metadata |
| `POST /responses` | submit an attempt (idempotent) |
| `GET  /responses/me?page_key=` | the caller's latest attempt per question |
| `POST /events` | batch ingest (1–50 events) |
| `POST /ai/chat` | context-aware tutor |
| `POST /ai/activity` | named-prompt activities (fact-or-fiction, design review, …) |
| `GET  /health`, `GET /health/ready` | liveness / readiness (DB round-trip + migration head check) |
| `GET  /admin/users`, `/admin/responses`, `/admin/analytics/summary`, `/admin/export/{dataset}.csv` | instructor/admin only |

Cross-cutting: `extra='forbid'` on every request schema, explicit `response_model` on every route,
1MB body cap at the proxy and a per-route field-length cap, and `409` on idempotency-key conflicts
with a differing payload.

---

## 8. AI service

```
React  ──POST /api/v1/ai/chat──▶  FastAPI
                                    ├── rate limit (per-user)
                                    ├── resolve page context from the content registry (server-side)
                                    ├── build messages from a named PromptTemplate
                                    ├── LLMService.chat(...)  ──▶ provider adapter
                                    │      ├── OpenAICompatibleProvider  (UF NaviGator, default)
                                    │      ├── GeminiProvider
                                    │      └── EchoProvider (no key configured → deterministic stub)
                                    ├── persist ai_messages (+ tokens, latency, model)
                                    └── return {content, conversation_id, usage}
```

- `LLMService` is the only place a provider SDK is touched. Adding or swapping a provider is one
  adapter class plus one env value; no route or UI changes.
- **Context is assembled on the server** from `backend/content/manifest.json`: module title, page
  title, learning objectives, current section, and the activity's own bounded result summary that the
  client may pass in `activity_context` (≤2KB, validated, no free-form user records). The learner's
  database rows, email, and name are never sent to the model.
- Guardrails: 30s timeout, 2 retries on 429/5xx with jittered backoff, output length cap, prompt-injection
  notice in the system prompt, and a `model_unavailable` error code that the UI renders as a friendly
  inline message rather than a failure state.
- Usage tracking: every call records prompt/completion tokens, latency, model, and outcome, keyed by
  `user_id` only.
- With no key configured, `EchoProvider` returns a clearly-labelled deterministic placeholder so the
  whole application (and the E2E suite) runs without credentials.

---

## 9. Progress and sessions

- On app load the client `POST`s a `session_started` event; the backend creates a `learning_session`
  and returns its id, which is attached to every subsequent response/event.
- `last_seen_at` is touched by the event batch endpoint. A session with no activity for 30 minutes is
  considered ended (closed lazily by the next batch, or explicitly by `session_ended` on `pagehide`).
- `page_progress.seconds_spent` accumulates **client-measured, server-validated** deltas: the client
  sends elapsed active time (paused when the tab is hidden) in increments ≤120s, and the service
  rejects implausible deltas. This gives usable time-on-task without trusting a raw client total.
- A page is `completed` when every `required` section id is in `sections_completed`. Module completion
  is derived (both pages completed) — not stored, so a content change recomputes it correctly.
- `GET /progress/me` returns `resume: {module_key, page_key, section_id}` so "continue where you left
  off" works across devices.

---

## 10. Analytics and research export

Recorded event types (backend-enforced allowlist):

```
session_started  session_ended
module_opened    module_completed
page_viewed      page_completed      page_section_completed
activity_started activity_completed  activity_reset
question_viewed  question_answered
prediction_submitted  simulation_run  parameter_changed
hint_opened      explanation_opened
ai_tutor_opened  ai_message_sent
navigation
```

These support the intended research questions directly: completion funnels
(`page_viewed` → `page_completed`), drop-off points (last event per session), time-on-task
(`page_progress.seconds_spent` + event timestamps), difficulty (`question_responses.is_correct`
grouped by `question_key`), within-module improvement (`attempt_no` trajectory), parameter
exploration (`parameter_changed.metadata`), tutor usage (`ai_messages` per user/page), and
path analysis (ordered event stream per `learning_session_id`).

`GET /admin/export/{events|responses|progress}.csv` streams pseudonymized rows (`user_id` UUID only).
No dashboard ships in v1 — the priority is clean, well-typed collection.

---

## 11. Security posture

| Control | Implementation |
| --- | --- |
| Transport | HTTPS terminated at Caddy with automatic certs; HSTS; Uvicorn bound to 127.0.0.1. |
| CORS | Explicit origin allowlist from `CORS_ORIGINS`; `allow_credentials=true`; no wildcard permitted when `ENVIRONMENT=production`. |
| CSRF | Refresh/logout require a double-submit token (`aip_csrf` readable cookie + `X-CSRF-Token` header). Access-token routes are immune (Authorization header is not sent cross-site automatically). |
| XSS | React escaping; no `dangerouslySetInnerHTML` anywhere; markdown-ish content is rendered through a whitelist inline formatter (bold/italic/code/link) that never emits raw HTML. `Content-Security-Policy` set at the proxy. |
| SQL injection | SQLAlchemy Core/ORM parameter binding exclusively; no string-interpolated SQL. |
| AuthZ | Server-side only. Every learner row is filtered by `user_id` from the token. Admin routes require a role check on the loaded user, not a claim alone. |
| Rate limiting | §4.4. |
| Request size | 1MB at the proxy; per-field `max_length` in Pydantic; events batch capped at 50; AI message capped at 4000 chars. |
| Secrets | Environment only. `.env` is gitignored; `.env.example` lists names with empty values. Nothing sensitive can reach the bundle: Vite only inlines `VITE_*`, and the only `VITE_*` variable is the API base URL. |
| DB least privilege | App role owns only the application schema; no superuser, no `CREATEDB`. Migrations may run as the same owner role. |
| Password storage | Argon2id, never logged. |
| Dependency hygiene | Pinned ranges, `pip-audit` / `npm audit` documented in the deployment runbook. |

---

## 12. Accessibility

- Semantic landmarks (`header`/`nav`/`main`/`aside`/`footer`), one `h1` per page, ordered headings.
- All controls are native (`button`, `input[type=range]`, `input[type=radio]`, `fieldset`/`legend`);
  custom widgets add ARIA only where native semantics are absent (tab lists, disclosure).
- Visible `:focus-visible` ring (3:1 against both adjacent colors) on every interactive element;
  skip-to-content link; no keyboard traps in the AI drawer (focus trap with Escape to close).
- Charts: `role="img"` with a generated `aria-label` summary, a keyboard-reachable "show data table"
  disclosure for every visualization, and encoding by shape/label/pattern in addition to color.
- Sliders announce value + unit via `aria-valuetext`; simulator outcomes are announced in an
  `aria-live="polite"` region so a screen-reader user perceives the change a sighted user sees.
- Contrast ≥4.5:1 for text and ≥3:1 for UI/graphical objects in both themes.
- `prefers-reduced-motion: reduce` removes transitions and any auto-advancing behavior.

---

## 13. Performance

- Route-level `lazy()` per page; each module page and each heavy activity is a separate chunk.
- Content is plain TS objects tree-shaken per page, so Module 5's imaging content is not in Module 1's chunk.
- Simulations are pure functions memoized with `useMemo`; slider drags mutate one number and repaint
  an SVG — no network, no re-fetch, no server compute.
- TanStack Query caches module/page metadata (`staleTime` 5 min) so back-navigation is instant.
- Backend: async SQLAlchemy with a pooled asyncpg connection (`pool_size=10, max_overflow=10`),
  indexed queries only, `GET /modules` returns a single joined query, event ingest is one
  multi-row insert per batch.
- Static assets get long-lived immutable cache headers from `netlify.toml`; `index.html` is `no-cache`.

---

## 14. Canvas / LTI 1.3 readiness

Already in place:

- `user_identities(provider, provider_subject)` with `canvas_lti` in the provider enum.
- Embed mode (`?embed=1` or iframe detection) that hides global chrome, keeps deep links working,
  and avoids fixed-viewport layout.
- Deep-linkable URLs for every page: `/modules/:moduleKey/:pageKey` (plus `?embed=1`).
- All cookies `SameSite=None; Secure`, which is what a Canvas iframe requires.
- A consistent authenticated-user representation (`GET /users/me`) that says nothing about *how* the
  user authenticated, so the frontend is provider-agnostic.

Remaining work when institutional credentials arrive (marked `TODO(lti)` in code):

1. `POST /lti/login` (OIDC third-party init) and `POST /lti/launch` (validate `id_token` against
   Canvas JWKS, `nonce`/`state` replay protection, platform registration table).
2. Map the validated launch to `user_identities(canvas_lti, <iss>|<sub>)` → existing or new `users` row,
   then issue the same session pair the local flow issues.
3. Deep Linking response for course-module placement.
4. Optional AGS: post `question_responses`-derived scores to the Canvas line item.

None of this requires a schema rewrite or a frontend restructure.

---

## 15. Testing strategy

| Layer | Tool | Coverage |
| --- | --- | --- |
| Backend unit/integration | pytest + httpx `ASGITransport` + a real Postgres test DB | register/login/refresh/logout, rotation reuse detection, rate limits, `extra='forbid'` rejection of client `user_id`, response append-only attempts + idempotency, event ingest + allowlist, progress computation, role guards, AI route with the stub provider, health/readiness |
| Frontend unit | Vitest + Testing Library | design-system primitives, question components per type, autosave state machine, analytics batching/debounce, auth context refresh, progress rendering, two representative activities |
| E2E | Playwright | register → open module → run activity → answer question → verify `Saved` → reload → state restored; plus embed-mode smoke and keyboard-only navigation of a question block |

---

## 16. Deployment

Detailed runbook in `docs/deployment.md`. Summary:

- **Frontend:** Netlify builds `frontend/` with `npm ci && npm run build`, publishes `dist`, SPA
  fallback + security headers + immutable asset caching from `netlify.toml`, `VITE_API_BASE_URL` set
  per context.
- **Backend:** `deploy/aipassport-api.service` runs `uvicorn app.main:app --host 127.0.0.1 --port 8000`
  under a dedicated `aipassport` system user with `EnvironmentFile=/etc/aipassport/api.env`, hardening
  directives (`ProtectSystem=strict`, `NoNewPrivileges`, `PrivateTmp`), and `Restart=always`.
- **Proxy:** `deploy/Caddyfile` (primary) or `deploy/nginx.conf` for `api.<domain>` → 127.0.0.1:8000,
  with CSP/HSTS/`client_max_body_size 1m`.
- **Database:** existing PostgreSQL on localhost; app role, owned schema, `alembic upgrade head` on
  deploy; port 5432 stays closed in the security group.
