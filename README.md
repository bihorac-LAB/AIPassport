# AIPassport

An interactive course in artificial intelligence for clinical, biomedical, research, and
administrative professionals — most of whom are not programmers.

Seven modules, **exactly two learner-facing pages each**. Every page pairs short explanations with
something the learner actually does: move a decision threshold and watch the confusion matrix
respond, induce covariate shift and decide whether to retrain, step a convolution kernel across an
image one multiplication at a time. Every answer, activity result, and meaningful interaction is
persisted and attributable to an authenticated user.

This replaces the original Streamlit implementation, which is preserved under [`legacy/`](legacy/).

```
run.sh      one-command local development (setup, run, test, build, diagnose)
frontend/   React 19 + TypeScript + Vite SPA          → Netlify
backend/    FastAPI + SQLAlchemy 2 + Alembic          → Ubuntu 24.04 EC2
legacy/     the original Streamlit app, unchanged
deploy/     systemd unit, Caddyfile, nginx.conf
docs/       legacy-audit.md · architecture.md · deployment.md
```

| Document | What it covers |
| --- | --- |
| [`docs/legacy-audit.md`](docs/legacy-audit.md) | What the Streamlit app contained, the two-page consolidation for each module, and every content removal with its rationale |
| [`docs/architecture.md`](docs/architecture.md) | Frontend and backend design, database model, auth, telemetry, AI service, LTI readiness |
| [`docs/deployment.md`](docs/deployment.md) | Production runbook for Netlify + EC2 + PostgreSQL |

---

## The course

| # | Module | Page 1 · build the concept | Page 2 · apply it |
| --- | --- | --- | --- |
| 1 | Fundamentals | Demystifying AI | From Question to Model |
| 2 | Alignment | Principles in Tension | Quality and Safety |
| 3 | Data | Sourcing Data Responsibly | Preparing Data for AI |
| 4 | Machine Learning | How Models Learn | Evaluating and Explaining |
| 5 | Images | Images as Data | Enhancing and Analyzing |
| 6 | Generative AI | How Generative Models Work | Using Generative AI Responsibly |
| 7 | Impact Project | Design Your Study | Communicate and Review |

34 interactive activities, 34 questions with stable identifiers and versioned content, and nine
AI-powered coaching activities. Module 6 is new — the legacy application advertised it in navigation
and shipped no content for it.

---

## Local development

Prerequisites: **Node.js 22+**, **Python 3.12+**, and **PostgreSQL 16** running locally.

```bash
./run.sh
```

That is the whole thing. On a fresh clone it creates the PostgreSQL role and databases, generates
`backend/.env` (with freshly-generated secrets) and `frontend/.env`, installs both dependency trees,
runs the migrations, seeds the curriculum, and then starts both servers:

```
Web app     http://localhost:5173
API         http://127.0.0.1:8000
API docs    http://127.0.0.1:8000/docs
Readiness   http://127.0.0.1:8000/api/v1/health/ready
```

Both reload on file changes. Ctrl-C stops both — including `uvicorn --reload`'s worker, which is why
the script kills process trees rather than single PIDs.

| Command | What it does |
| --- | --- |
| `./run.sh` | Set up if needed, then start the API and the web app |
| `./run.sh setup` | Install dependencies, write `.env` files, migrate, seed |
| `./run.sh test` | Backend pytest + frontend typecheck + frontend unit tests |
| `./run.sh e2e` | Playwright suite (starts the API, builds and previews the frontend) |
| `./run.sh build` | Production build, including content validation |
| `./run.sh preview` | Serve the production bundle — exactly what Netlify publishes |
| `./run.sh seed` / `manifest` / `migrate` | Individual content and schema steps |
| `./run.sh status` / `logs` | What is running, readiness detail, follow both logs |
| `./run.sh stop` | Stop everything, and release the ports if a previous run crashed |
| `./run.sh doctor` | Diagnose a broken setup (versions, database, ports, project state) |
| `./run.sh reset-db` | **Destructive**: drop and recreate the dev database (asks to confirm) |

Ports and database names are overridable: `API_PORT=8001 WEB_PORT=5174 ./run.sh`.

**No LLM credential is required.** Without `LLM_API_KEY` or `GEMINI_API_KEY`, the AI tutor and the
nine AI activities return a clearly-labelled offline placeholder and everything else — including the
whole test suite — works normally. Add one to `backend/.env` to enable live AI.

<details>
<summary>Doing it by hand instead</summary>

```bash
# Database
sudo -u postgres psql <<'SQL'
CREATE ROLE aipassport LOGIN PASSWORD 'choose-a-local-password';
CREATE DATABASE aipassport      OWNER aipassport;
CREATE DATABASE aipassport_test OWNER aipassport;
SQL

# Backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
cp .env.example .env              # set DATABASE_URL, SECRET_KEY, HASH_SALT
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed
.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
cp .env.example .env              # VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

</details>

---

## Content authoring

Educational copy lives in typed structures under `frontend/src/content/`, never inside component
JSX. To change wording, edit the module file. To change a question, edit it and **bump its
`version`** so responses recorded against the old wording stay interpretable.

```
frontend/src/content/module-4.ts   ← copy, questions, section order for Module 4
frontend/src/activities/module4.tsx ← the interactive components that module uses
frontend/src/activities/registry.ts ← maps an activity key to a lazily-loaded component
```

The same content is the single source of truth for the database:

```bash
cd frontend && npm run export:manifest   # writes backend/content/manifest.json
cd backend  && .venv/bin/python -m scripts.seed
```

`npm run build` runs the export first and **fails** if the content is structurally invalid — a module
without exactly two pages, a duplicate question key, a required section that does not exist. Seeding
is idempotent: rows are matched by stable key and updated in place, and a question removed from the
content is deactivated rather than deleted so its historical responses survive.

---

## Tests

```bash
./run.sh test    # 61 backend + typecheck + 34 frontend unit
./run.sh e2e     # 4 end-to-end specs against the real API and database
```

The backend suite builds its schema with `alembic upgrade head`, so it also proves the migrations
work from a clean database.

The E2E suite covers the critical flow — register → open module → run activity → answer question →
response saved → event saved → reload → state and progress restored — plus embed-mode layout and
keyboard-only operation of a question block.

> The default rate limits (5 registrations/hour/IP) block repeated E2E runs from one machine, so the
> `backend/.env` that `./run.sh` generates raises them. Production keeps the shipped defaults —
> `backend/.env.example` documents both.

---

## How the important guarantees are enforced

**A learner's work is always attributed to the authenticated user.** No write endpoint declares a
`user_id`, and every request schema sets `extra='forbid'` — so a client that sends one gets a 422
rather than being trusted. The owning user comes from the access token, server-side, every time.
Tested in `backend/tests/test_learning.py::test_client_supplied_user_id_is_rejected`.

**Responses are append-only.** Re-answering creates `attempt_no + 1`; the previous attempt is
retained and only its `is_final` flag moves. Research analysis gets the whole trajectory, not just
the last state.

**Correctness is decided on the server.** The client renders feedback but never computes it.

**No secret reaches the browser.** The only `VITE_*` variable is the API base URL. The LLM
credential, the database URL, and the JWT signing key exist solely in the backend process
environment. The browser never contacts PostgreSQL.

**Sessions survive a refresh without a long-lived token in `localStorage`.** The access token lives
in module memory (15 min); continuity comes from an `HttpOnly` refresh cookie with rotation and
reuse detection — replaying a rotated token revokes the whole session family.

**Telemetry is bounded.** Event types are a server-side enum, so an unrecognized type is rejected at
validation. Slider drags emit at most one `parameter_changed` per 1500ms of quiet plus one
`activity_completed` with the final parameter set — the legacy app's per-rerun churn is gone.

**PII is separated from learning data.** `users` is the only table with an email or a name. Every
learning and telemetry table references `user_id` alone, so the research export is pseudonymous by
construction.

---

## Accessibility

Targets WCAG 2.1 AA. Native controls throughout (`fieldset`/`legend`, `input[type=range]`, real
radios and checkboxes); visible focus rings; sliders announce a formatted `aria-valuetext`; simulator
outcomes update an `aria-live` region so a screen-reader user perceives the change a sighted user
sees; every chart carries a generated description plus a keyboard-reachable data table; state is
never signalled by color alone; `prefers-reduced-motion` removes all transitions. Both themes meet
4.5:1 for text and 3:1 for UI objects.

---

## Running the legacy Streamlit app

Preserved verbatim. It uses repo-relative asset paths, so run it from inside `legacy/`:

```bash
cd legacy
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# .streamlit/secrets.toml needs NAVIGATOR_TOOLKIT_API_KEY for the 1.1 and 7.x activities
streamlit run aipassport_notebooks.py
```

---

## Not yet built

`docs/deployment.md §8` lists the LTI 1.3 work, which is blocked on UF supplying a client ID,
deployment ID, and key set. The data model, embed mode, deep-linkable URLs, and cookie policy already
support it; adding Canvas requires no schema change and no frontend restructuring.

Email delivery is also pending real SMTP credentials. Password-reset and verification tokens are
generated and stored correctly today; without `SMTP_HOST` the token is logged at DEBUG so the flow is
testable end to end locally.
