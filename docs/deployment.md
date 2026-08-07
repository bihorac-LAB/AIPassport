# Deployment Runbook

Target topology:

```
Browser / Canvas iframe
        │
        ▼
Netlify  (static SPA)
        │  HTTPS
        ▼
Caddy or Nginx  :443   api.<domain>          ← the only public listener
        │
        ▼
Uvicorn / FastAPI  127.0.0.1:8000            ← systemd, never public
        │
        ▼
PostgreSQL 16      127.0.0.1:5432            ← localhost only, port never opened
        │
        └── outbound HTTPS → LLM provider
```

Placeholders to replace: `api.aipassport.example.edu`, `aipassport.netlify.app`, and the
`ops@example.edu` ACME contact.

---

## 1. Prerequisites

- Ubuntu 24.04 EC2 instance with PostgreSQL 16 already installed (it is).
- Security group inbound: **80 and 443 only** (plus SSH from your admin range). Never 5432, never 8000.
- A DNS `A`/`AAAA` record for `api.<domain>` pointing at the instance.
- A Netlify site connected to this repository.

---

## 2. PostgreSQL

PostgreSQL already exists on the instance. Confirm it is not listening publicly:

```bash
sudo grep -E "^listen_addresses" /etc/postgresql/16/main/postgresql.conf   # absent or 'localhost'
sudo ss -lntp | grep 5432                                                  # 127.0.0.1:5432 only
```

Create the application role and database with **least privilege** — the app role owns only its own
schema and is not a superuser:

```bash
sudo -u postgres psql <<'SQL'
CREATE ROLE aipassport LOGIN PASSWORD 'GENERATE_A_STRONG_PASSWORD';
CREATE DATABASE aipassport OWNER aipassport;
SQL

# No CREATEDB, no CREATEROLE, no SUPERUSER. Verify:
sudo -u postgres psql -tAc \
  "SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname='aipassport';"
# expect: f|f|f
```

> **Existing data:** migration `0001` aborts with an explanation if any of its table names already
> exist, so it can never overwrite an unrelated database. If the database was already migrated by an
> earlier deploy, run `alembic stamp head` instead of `upgrade`.

---

## 3. Backend on EC2

```bash
# Dedicated unprivileged service user with no login shell.
sudo useradd --system --home /opt/aipassport --shell /usr/sbin/nologin aipassport
sudo install -d -o aipassport -g aipassport /opt/aipassport

sudo -u aipassport git clone https://github.com/bihorac-LAB/AIPassport.git /opt/aipassport
cd /opt/aipassport/backend
sudo -u aipassport python3 -m venv .venv
sudo -u aipassport .venv/bin/pip install --upgrade pip
sudo -u aipassport .venv/bin/pip install -r requirements.txt
```

### Environment file

Secrets live outside the repository, root-owned, group-readable by the service user only:

```bash
sudo install -d -m 0750 -o root -g aipassport /etc/aipassport
sudo install -m 0640 -o root -g aipassport backend/.env.example /etc/aipassport/api.env
sudo nano /etc/aipassport/api.env
```

Minimum production values:

```ini
ENVIRONMENT=production
SECRET_KEY=<python3 -c "import secrets;print(secrets.token_urlsafe(48))">
HASH_SALT=<a DIFFERENT value from the same command>

DATABASE_URL=postgresql+asyncpg://aipassport:STRONG_PASSWORD@localhost:5432/aipassport

FRONTEND_URL=https://aipassport.netlify.app
CORS_ORIGINS=https://aipassport.netlify.app

# Cross-site (Netlify → EC2) and Canvas iframes both require this pairing.
COOKIE_SAMESITE=none
COOKIE_SECURE=true

# UF NaviGator Toolkit, or set GEMINI_API_KEY instead. Without either, the AI features fall back
# to a clearly-labelled offline stub and everything else works.
LLM_API_KEY=<key>

# Keep the shipped defaults. Raising these is only appropriate in a test environment.
# RATE_LIMIT_REGISTER_PER_HOUR=5
```

The application **refuses to start** in production with a default `SECRET_KEY`, a wildcard
`CORS_ORIGINS`, or `COOKIE_SECURE=false`. That is intentional.

### Migrate, seed, and start

```bash
cd /opt/aipassport/backend
sudo -u aipassport env $(grep -v '^#' /etc/aipassport/api.env | xargs) .venv/bin/alembic upgrade head
sudo -u aipassport env $(grep -v '^#' /etc/aipassport/api.env | xargs) .venv/bin/python -m scripts.seed

sudo cp ../deploy/aipassport-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now aipassport-api
sudo systemctl status aipassport-api --no-pager
```

The unit runs `alembic upgrade head` in `ExecStartPre`, so a restart after a deploy applies pending
migrations automatically. `scripts/seed.py` is idempotent — run it after any content change.

---

## 4. Reverse proxy

**Caddy (recommended — automatic certificates):**

```bash
sudo apt install -y caddy
sudo cp /opt/aipassport/deploy/Caddyfile /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile          # set your hostname and ACME email
sudo systemctl reload caddy
```

**Nginx alternative:**

```bash
sudo cp /opt/aipassport/deploy/nginx.conf /etc/nginx/sites-available/aipassport-api
sudo ln -s /etc/nginx/sites-available/aipassport-api /etc/nginx/sites-enabled/
sudo certbot --nginx -d api.aipassport.example.edu
sudo nginx -t && sudo systemctl reload nginx
```

Verify the boundary:

```bash
curl https://api.aipassport.example.edu/health          # {"status":"ok",...}
curl https://api.aipassport.example.edu/health/ready     # every critical check true
curl http://<public-ip>:8000/health                      # MUST fail — app port is not public
```

`/docs` is disabled when `ENVIRONMENT=production` unless you set `ENABLE_DOCS=true`.

---

## 5. Frontend on Netlify

`frontend/netlify.toml` carries the build command, SPA fallback, security headers, and cache policy.
In the Netlify UI:

1. **Base directory** `frontend` · **Build command** `npm ci && npm run build` · **Publish** `dist`.
2. Set `VITE_API_BASE_URL=https://api.aipassport.example.edu` for the production context.
3. Update the `connect-src` and `frame-ancestors` entries in `netlify.toml`'s CSP to your real API
   host and Canvas host.

`VITE_API_BASE_URL` is the only variable the browser receives. **Vite inlines every `VITE_*` value
into the published JavaScript**, so a database URL, an LLM key, or a JWT secret placed there would be
world-readable.

Confirm after the first deploy:

```bash
curl -s https://aipassport.netlify.app/assets/index-*.js | grep -ciE "postgres://|sk-|SECRET_KEY"
# expect 0
```

`npm run build` regenerates `backend/content/manifest.json` from the typed content and fails the
build if the content is structurally invalid (a module without exactly two pages, a duplicate
question key, a required section that does not exist).

---

## 6. Deploying an update

```bash
cd /opt/aipassport
sudo -u aipassport git pull
cd backend
sudo -u aipassport .venv/bin/pip install -r requirements.txt
sudo systemctl restart aipassport-api      # ExecStartPre applies migrations
# After a content change:
sudo -u aipassport env $(grep -v '^#' /etc/aipassport/api.env | xargs) .venv/bin/python -m scripts.seed
```

Netlify redeploys the frontend from the same push.

---

## 7. Operations

```bash
sudo journalctl -u aipassport-api -f              # structured JSON logs in production
sudo journalctl -u aipassport-api -p err --since today
curl -s https://api.aipassport.example.edu/health/ready | jq
```

Readiness reports `database`, `migrations`, `content`, `content_manifest`, and `llm`. The LLM check
is informational — a missing model credential degrades the AI features to a labelled offline stub
and never fails readiness.

Logs never contain passwords, tokens, cookies, or email addresses. Authentication failures record a
non-reversible email tag so they can be correlated without exposing the address.

**Backups** (nothing here is application-specific, but do not skip it):

```bash
sudo -u postgres pg_dump -Fc aipassport > /var/backups/aipassport-$(date +%F).dump
```

**Dependency audit**, before each release:

```bash
cd /opt/aipassport/backend && .venv/bin/pip install pip-audit && .venv/bin/pip-audit
cd /opt/aipassport/frontend && npm audit --omit=dev
```

---

## 8. Canvas / LTI 1.3 (not yet enabled)

Everything below already works, so enabling LTI later is additive:

- `user_identities(provider, provider_subject)` with `canvas_lti` in the provider enum.
- Deep-linkable page URLs: `/modules/:moduleKey/:pageKey`, plus `?embed=1` for a frame.
- `SameSite=None; Secure` cookies, which a Canvas iframe requires.
- Layout with no `100vh` assumptions and no parent-document scripting.

Remaining work when UF supplies the client ID, deployment ID, and key set (marked `TODO(lti)` in
code):

1. `POST /lti/login` (OIDC third-party init) and `POST /lti/launch` (validate `id_token` against
   Canvas JWKS, with nonce/state replay protection and a platform-registration table).
2. Map the validated launch to `user_identities(canvas_lti, "<iss>|<sub>")`, link it to an existing
   `users` row or create one, then issue the same token pair the local flow issues.
3. Deep Linking response for course-module placement.
4. Optional Assignment and Grade Services, posting scores derived from `question_responses`.

No schema rewrite and no frontend restructuring is required for any of these.

---

## 9. Rollback

```bash
cd /opt/aipassport && sudo -u aipassport git checkout <previous-tag>
cd backend && sudo -u aipassport .venv/bin/pip install -r requirements.txt
# Only if the release added a migration you need to undo:
sudo -u aipassport env $(grep -v '^#' /etc/aipassport/api.env | xargs) .venv/bin/alembic downgrade -1
sudo systemctl restart aipassport-api
```

Netlify rolls the frontend back from its Deploys list in one click. Because the frontend only reads
the API and never writes schema, the two can be rolled back independently.
