#!/usr/bin/env bash
#
# AIPassport development runner.
#
#   ./run.sh              start the API and the web app together (sets itself up first)
#   ./run.sh setup        install dependencies, create .env files, migrate, seed
#   ./run.sh db           create the local PostgreSQL role and databases (uses sudo)
#   ./run.sh migrate      alembic upgrade head
#   ./run.sh seed         load modules/pages/questions from the content manifest
#   ./run.sh manifest     regenerate backend/content/manifest.json from the typed content
#   ./run.sh test         backend + frontend unit tests
#   ./run.sh e2e          Playwright end-to-end suite (starts the API if needed)
#   ./run.sh build        production build of the frontend
#   ./run.sh preview      serve the production build (what E2E and Netlify run)
#   ./run.sh stop         stop anything this script started
#   ./run.sh status       show what is running and whether the API is healthy
#   ./run.sh logs         follow the API and web logs
#   ./run.sh doctor       check prerequisites and diagnose a broken setup
#   ./run.sh reset-db     DESTRUCTIVE: drop and recreate the dev database
#
# Environment overrides: API_PORT (8000), WEB_PORT (5173), PREVIEW_PORT (4173),
#                        DB_NAME (aipassport), DB_USER (aipassport)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
RUN_DIR="$ROOT/.run"
VENV="$BACKEND/.venv"
PY="$VENV/bin/python"

API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"
PREVIEW_PORT="${PREVIEW_PORT:-4173}"
DB_NAME="${DB_NAME:-aipassport}"
DB_TEST_NAME="${DB_TEST_NAME:-${DB_NAME}_test}"
DB_USER="${DB_USER:-aipassport}"

# ── Output ────────────────────────────────────────────────────────────────────

if [[ -t 1 ]]; then
  B=$'\033[1m'; DIM=$'\033[2m'; R=$'\033[0m'
  BLUE=$'\033[34m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'
else
  B=''; DIM=''; R=''; BLUE=''; GREEN=''; YELLOW=''; RED=''
fi

step() { printf '%s\n' "${B}${BLUE}==>${R} ${B}$*${R}"; }
info() { printf '    %s\n' "$*"; }
ok()   { printf '    %s✓%s %s\n' "$GREEN" "$R" "$*"; }
warn() { printf '    %s!%s %s\n' "$YELLOW" "$R" "$*"; }
die()  { printf '%s\n' "${RED}${B}error:${R} $*" >&2; exit 1; }

# ── Prerequisites ─────────────────────────────────────────────────────────────

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed.${2:+ $2}"
}

check_prereqs() {
  require_cmd python3 "Install Python 3.12 or newer."
  require_cmd node "Install Node.js 22 or newer (https://nodejs.org)."
  require_cmd npm
  require_cmd curl

  local py_ok node_ok
  py_ok=$(python3 -c 'import sys; print(1 if sys.version_info >= (3, 12) else 0)')
  [[ "$py_ok" == "1" ]] || die "Python 3.12+ required; found $(python3 -V 2>&1)."
  node_ok=$(node -e 'process.stdout.write(Number(process.versions.node.split(".")[0]) >= 20 ? "1" : "0")')
  [[ "$node_ok" == "1" ]] || die "Node.js 20+ required; found $(node -v)."
}

# ── Process helpers ───────────────────────────────────────────────────────────
#
# Servers run as plain background jobs of this script (deliberately not via setsid), so:
#   * $! is the real server pid, which keeps the pid files accurate; and
#   * in a terminal, Ctrl-C reaches them through the shared process group.
# `uvicorn --reload` and `npm run dev` each fork a worker, so shutdown kills the whole tree.

pid_file() { printf '%s/%s.pid' "$RUN_DIR" "$1"; }

alive() { [[ -n "${1:-}" ]] && kill -0 "$1" 2>/dev/null; }

kill_tree() {
  local pid="$1" sig="${2:-TERM}" child
  for child in $(pgrep -P "$pid" 2>/dev/null || true); do
    kill_tree "$child" "$sig"
  done
  kill "-$sig" "$pid" 2>/dev/null || true
}

stop_pid() {
  local pid="$1" i
  alive "$pid" || return 0
  kill_tree "$pid" TERM
  for i in $(seq 1 24); do
    alive "$pid" || return 0
    sleep 0.25
  done
  kill_tree "$pid" KILL
}

listener_pids() {
  local port="$1"
  # No listener is a normal answer, not an error: `grep` exits 1 when it matches nothing and
  # `pipefail` would turn that into a script-aborting failure under `set -e`.
  if command -v ss >/dev/null 2>&1; then
    ss -lntp "sport = :$port" 2>/dev/null | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u || true
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | sort -u || true
  fi
  return 0
}

port_busy() {
  if [[ -n "$(listener_pids "$1")" ]]; then
    return 0
  fi
  # ss/lsof may be missing or unprivileged; fall back to a connect probe.
  if (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; then
    exec 3>&-
    return 0
  fi
  return 1
}

stop_service() {
  local name="$1" port="${2:-}" file pid leftover
  file="$(pid_file "$name")"

  if [[ -f "$file" ]]; then
    pid="$(cat "$file" 2>/dev/null || true)"
    if alive "$pid"; then
      stop_pid "$pid"
      ok "stopped $name (pid $pid)"
    fi
    rm -f "$file"
  fi

  # Anything still holding the port is a leftover from a crash or a manual start; release it so
  # the next ./run.sh is not blocked by a stale server.
  if [[ -n "$port" ]]; then
    for leftover in $(listener_pids "$port"); do
      alive "$leftover" || continue
      stop_pid "$leftover"
      ok "released port $port (pid $leftover)"
    done
  fi
  return 0
}

cmd_stop() {
  step "Stopping services"
  stop_service api "$API_PORT"
  stop_service web "$WEB_PORT"
  stop_service preview "$PREVIEW_PORT"
  info "done"
}

CLEANED=0

cleanup() {
  if [[ "$CLEANED" -eq 1 ]]; then
    return 0
  fi
  CLEANED=1
  # Kill this shell's own background jobs (the log tails) so nothing keeps the script alive.
  local job
  for job in $(jobs -p 2>/dev/null || true); do
    kill "$job" 2>/dev/null || true
  done
  printf '\n'
  cmd_stop
}

wait_for_http() {
  local url="$1" tries="${2:-80}" i
  for i in $(seq 1 "$tries"); do
    curl -fsS --max-time 2 "$url" >/dev/null 2>&1 && return 0
    sleep 0.5
  done
  return 1
}

# ── Database ──────────────────────────────────────────────────────────────────

db_url_from_env() {
  # Read DATABASE_URL without sourcing the file, which may contain shell metacharacters.
  [[ -f "$BACKEND/.env" ]] || return 1
  sed -n 's/^DATABASE_URL=//p' "$BACKEND/.env" | tail -n1
}

db_password_from_env() {
  local url
  url="$(db_url_from_env)" || return 1
  printf '%s' "$url" | sed -n 's#.*://[^:]*:\([^@]*\)@.*#\1#p'
}

db_reachable() {
  command -v psql >/dev/null 2>&1 || return 1
  local pw
  pw="$(db_password_from_env)" || return 1
  if [[ -z "$pw" ]]; then
    return 1
  fi
  PGPASSWORD="$pw" psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" -tAc 'select 1' >/dev/null 2>&1
}

cmd_db() {
  step "Provisioning PostgreSQL"
  require_cmd psql "Install PostgreSQL 16: sudo apt install postgresql"

  if ! (command -v pg_isready >/dev/null 2>&1 && pg_isready -q -h 127.0.0.1 2>/dev/null); then
    warn "PostgreSQL is not accepting connections on 127.0.0.1:5432."
    info "Try: sudo systemctl start postgresql"
  fi

  local pw
  pw="$(db_password_from_env || true)"
  if [[ -z "$pw" ]]; then
    pw="$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))')"
    info "Generated a local development password for role '$DB_USER'."
  fi

  info "Creating the role and databases (needs sudo for the postgres superuser)."
  sudo -u postgres psql --quiet -v ON_ERROR_STOP=1 <<SQL
DO \$do\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE ROLE $DB_USER LOGIN PASSWORD '$pw';
  ELSE
    ALTER ROLE $DB_USER WITH LOGIN PASSWORD '$pw';
  END IF;
END
\$do\$;
SQL

  local name
  for name in "$DB_NAME" "$DB_TEST_NAME"; do
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$name'" | grep -q 1; then
      ok "database $name exists"
    else
      sudo -u postgres createdb -O "$DB_USER" "$name"
      ok "created database $name"
    fi
  done

  write_backend_env "$pw"
  if db_reachable; then
    ok "connected to $DB_NAME as $DB_USER"
  else
    die "Created the role but still cannot connect. Run './run.sh doctor'."
  fi
}

cmd_reset_db() {
  step "Resetting the development database"
  warn "This DROPS the database '$DB_NAME' and every learner record in it."
  local confirm
  read -r -p "    Type '$DB_NAME' to confirm: " confirm
  [[ "$confirm" == "$DB_NAME" ]] || die "Not confirmed; nothing was changed."
  cmd_stop
  sudo -u postgres dropdb --if-exists "$DB_NAME"
  sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"
  ok "recreated $DB_NAME (empty)"
  cmd_migrate
  cmd_seed
}

# ── Environment files ─────────────────────────────────────────────────────────

write_backend_env() {
  local pw="$1" secret='' salt=''
  if [[ -f "$BACKEND/.env" ]]; then
    # Preserve existing secrets so sessions and reset tokens survive a re-run.
    secret="$(sed -n 's/^SECRET_KEY=//p' "$BACKEND/.env" | tail -n1)"
    salt="$(sed -n 's/^HASH_SALT=//p' "$BACKEND/.env" | tail -n1)"
  fi
  if [[ -z "$secret" ]]; then
    secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  fi
  if [[ -z "$salt" ]]; then
    salt="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  fi

  cat > "$BACKEND/.env" <<ENV
# Generated by ./run.sh for LOCAL DEVELOPMENT ONLY.
# Production values belong in /etc/aipassport/api.env — see docs/deployment.md.
ENVIRONMENT=development

SECRET_KEY=$secret
HASH_SALT=$salt

DATABASE_URL=postgresql+asyncpg://$DB_USER:$pw@127.0.0.1:5432/$DB_NAME
TEST_DATABASE_URL=postgresql+asyncpg://$DB_USER:$pw@127.0.0.1:5432/$DB_TEST_NAME

FRONTEND_URL=http://localhost:$WEB_PORT
CORS_ORIGINS=http://localhost:$WEB_PORT,http://127.0.0.1:$WEB_PORT,http://localhost:$PREVIEW_PORT,http://127.0.0.1:$PREVIEW_PORT

COOKIE_SAMESITE=lax
COOKIE_SECURE=false
LOG_LEVEL=INFO

# No LLM credential is required: the AI tutor and the AI activities fall back to a clearly
# labelled offline stub. Set one of these to enable live AI.
# LLM_API_KEY=
# GEMINI_API_KEY=

# Local and E2E only. The production defaults (5 registrations per hour per IP) block repeated
# test runs from a single machine.
RATE_LIMIT_REGISTER_PER_HOUR=500
RATE_LIMIT_LOGIN_PER_IP=500
RATE_LIMIT_LOGIN_PER_EMAIL=200
ENV
  chmod 600 "$BACKEND/.env"
  ok "wrote backend/.env"
}

ensure_frontend_env() {
  if [[ ! -f "$FRONTEND/.env" ]]; then
    printf 'VITE_API_BASE_URL=http://127.0.0.1:%s\n' "$API_PORT" > "$FRONTEND/.env"
    ok "wrote frontend/.env"
  fi
}

# ── Setup ─────────────────────────────────────────────────────────────────────

install_backend() {
  if [[ ! -x "$PY" ]]; then
    step "Creating the Python virtual environment"
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet --upgrade pip
  fi
  local stamp="$VENV/.requirements-stamp" current
  current="$(sha256sum "$BACKEND/requirements-dev.txt" | cut -d' ' -f1)"
  if [[ ! -f "$stamp" ]] || [[ "$(cat "$stamp")" != "$current" ]]; then
    step "Installing backend dependencies"
    "$VENV/bin/pip" install --quiet -r "$BACKEND/requirements-dev.txt"
    printf '%s' "$current" > "$stamp"
    ok "backend dependencies installed"
  else
    ok "backend dependencies up to date"
  fi
}

install_frontend() {
  if [[ ! -d "$FRONTEND/node_modules" ]] \
    || [[ "$FRONTEND/package-lock.json" -nt "$FRONTEND/node_modules" ]]; then
    step "Installing frontend dependencies"
    (cd "$FRONTEND" && npm install --no-fund --no-audit)
    touch "$FRONTEND/node_modules"
    ok "frontend dependencies installed"
  else
    ok "frontend dependencies up to date"
  fi
}

cmd_manifest() {
  step "Exporting the content manifest"
  # The typed content under frontend/src/content is the single source of truth; the backend
  # seeder reads the JSON this writes. It fails loudly if the content is structurally invalid.
  (cd "$FRONTEND" && npm run --silent export:manifest)
}

cmd_migrate() {
  step "Applying database migrations"
  (cd "$BACKEND" && "$VENV/bin/alembic" upgrade head)
  ok "schema at head"
}

cmd_seed() {
  [[ -f "$BACKEND/content/manifest.json" ]] || cmd_manifest
  step "Seeding modules, pages, and questions"
  (cd "$BACKEND" && "$PY" -m scripts.seed)
}

cmd_setup() {
  check_prereqs

  if [[ ! -f "$BACKEND/.env" ]]; then
    cmd_db
  elif ! db_reachable; then
    warn "backend/.env exists but the database is unreachable; reprovisioning."
    cmd_db
  else
    ok "backend/.env present and the database is reachable"
  fi

  ensure_frontend_env
  install_backend
  install_frontend
  cmd_manifest
  cmd_migrate
  cmd_seed
  printf '\n'
  ok "Setup complete. Run ${B}./run.sh${R} to start the app."
}

needs_setup() {
  [[ ! -x "$PY" ]] || [[ ! -d "$FRONTEND/node_modules" ]] || [[ ! -f "$BACKEND/.env" ]] \
    || [[ ! -f "$BACKEND/content/manifest.json" ]]
}

setup_if_needed() {
  if needs_setup; then
    info "First run detected; setting up."
    cmd_setup
  else
    check_prereqs
    ensure_frontend_env
  fi
}

# ── Starting servers ──────────────────────────────────────────────────────────

start_api() {
  if port_busy "$API_PORT"; then
    if curl -fsS --max-time 2 "http://127.0.0.1:$API_PORT/health" >/dev/null 2>&1; then
      ok "API already running on port $API_PORT"
      return 0
    fi
    die "Port $API_PORT is in use by something that is not the AIPassport API.
       Run './run.sh stop', or start on another port: API_PORT=8001 ./run.sh"
  fi

  mkdir -p "$RUN_DIR"
  step "Starting the API on http://127.0.0.1:$API_PORT"
  ( cd "$BACKEND" && exec "$VENV/bin/uvicorn" app.main:app \
      --host 127.0.0.1 --port "$API_PORT" --reload ) >"$RUN_DIR/api.log" 2>&1 &
  printf '%s' "$!" > "$(pid_file api)"

  if wait_for_http "http://127.0.0.1:$API_PORT/health"; then
    ok "API healthy"
  else
    warn "API did not become healthy. Last 30 log lines:"
    tail -n 30 "$RUN_DIR/api.log" | sed 's/^/      /'
    die "API failed to start."
  fi
}

start_web() {
  if port_busy "$WEB_PORT"; then
    ok "port $WEB_PORT is already serving something"
    return 0
  fi
  mkdir -p "$RUN_DIR"
  step "Starting the web app on http://localhost:$WEB_PORT"
  ( cd "$FRONTEND" && exec npm run --silent dev -- --port "$WEB_PORT" --strictPort ) \
    >"$RUN_DIR/web.log" 2>&1 &
  printf '%s' "$!" > "$(pid_file web)"

  if wait_for_http "http://127.0.0.1:$WEB_PORT/"; then
    ok "web app ready"
  else
    warn "Web app did not start. Last 30 log lines:"
    tail -n 30 "$RUN_DIR/web.log" | sed 's/^/      /'
    die "Web app failed to start."
  fi
}

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_dev() {
  setup_if_needed

  # Cleanup must run on every exit path: Ctrl-C, SIGTERM, a closed terminal, or an error under
  # `set -e`. Without the EXIT trap a stray uvicorn keeps holding the port.
  trap 'cleanup; exit 0' INT TERM HUP
  trap 'cleanup' EXIT

  start_api
  start_web

  local ai_mode
  if grep -qE '^(LLM_API_KEY|GEMINI_API_KEY)=..*' "$BACKEND/.env"; then
    ai_mode="live"
  else
    ai_mode="offline stub (no credential set)"
  fi

  cat <<BANNER

  ${B}${GREEN}AIPassport is running.${R}

    Web app     ${B}http://localhost:$WEB_PORT${R}
    API         http://127.0.0.1:$API_PORT
    API docs    http://127.0.0.1:$API_PORT/docs
    Readiness   http://127.0.0.1:$API_PORT/api/v1/health/ready

    AI features $ai_mode
    Logs        .run/api.log  .run/web.log

  ${DIM}Both servers reload on file changes. Press Ctrl-C to stop them.${R}

BANNER

  # Mirror both logs with a prefix so it is obvious which server said what.
  tail -n 0 -F "$RUN_DIR/api.log" 2>/dev/null | sed "s/^/${BLUE}[api]${R} /" &
  tail -n 0 -F "$RUN_DIR/web.log" 2>/dev/null | sed "s/^/${GREEN}[web]${R} /" &

  # Block until a server exits. `wait -n` with explicit pids returns the moment one dies, so a
  # crash surfaces immediately instead of after a polling interval.
  local api_pid web_pid
  api_pid="$(cat "$(pid_file api)" 2>/dev/null || true)"
  web_pid="$(cat "$(pid_file web)" 2>/dev/null || true)"

  if [[ -n "$api_pid" ]] && [[ -n "$web_pid" ]]; then
    wait -n "$api_pid" "$web_pid" 2>/dev/null || true
  else
    # One of them was already running before we started, so there is nothing of ours to wait on.
    while :; do sleep 3600; done
  fi

  # Only reached when a server exited on its own.
  local svc p
  for svc in api web; do
    p="$(cat "$(pid_file "$svc")" 2>/dev/null || true)"
    if ! alive "$p"; then
      warn "$svc exited unexpectedly; last lines of .run/$svc.log:"
      tail -n 20 "$RUN_DIR/$svc.log" 2>/dev/null | sed 's/^/      /'
    fi
  done
  exit 1
}

cmd_logs() {
  [[ -d "$RUN_DIR" ]] || die "Nothing has been started yet."
  trap 'exit 0' INT TERM
  tail -n 40 -F "$RUN_DIR/api.log" 2>/dev/null | sed "s/^/${BLUE}[api]${R} /" &
  tail -n 40 -F "$RUN_DIR/web.log" 2>/dev/null | sed "s/^/${GREEN}[web]${R} /" &
  wait
}

cmd_test() {
  setup_if_needed
  local failed=0

  step "Backend tests"
  # Builds its schema with Alembic against TEST_DATABASE_URL, so this also proves migrations
  # work from a clean database.
  (cd "$BACKEND" && "$PY" -m pytest -q) || failed=1

  step "Frontend typecheck"
  (cd "$FRONTEND" && npx --no-install tsc -b) || failed=1

  step "Frontend unit tests"
  (cd "$FRONTEND" && npm run --silent test) || failed=1

  printf '\n'
  if [[ "$failed" -eq 0 ]]; then
    ok "All tests passed."
  else
    die "Some tests failed; see the output above."
  fi
}

cmd_e2e() {
  setup_if_needed
  trap 'cleanup; exit 130' INT TERM HUP
  start_api

  if [[ ! -d "$HOME/.cache/ms-playwright" ]]; then
    step "Installing the Chromium browser (first run only)"
    (cd "$FRONTEND" && npx playwright install chromium --with-deps)
  fi

  step "Running the end-to-end suite"
  info "Playwright builds and previews the frontend itself."
  (cd "$FRONTEND" && npm run --silent e2e)
}

cmd_build() {
  setup_if_needed
  step "Building the frontend for production"
  # Regenerates the manifest and fails if the content is structurally invalid.
  (cd "$FRONTEND" && npm run --silent build)
  ok "output in frontend/dist"
}

cmd_preview() {
  cmd_build
  trap 'cleanup; exit 0' INT TERM HUP
  trap 'cleanup' EXIT
  start_api
  step "Serving the production build on http://localhost:$PREVIEW_PORT"
  info "This is the exact bundle Netlify would publish."
  (cd "$FRONTEND" && npx vite preview --port "$PREVIEW_PORT" --strictPort)
}

cmd_status() {
  step "Status"
  local anything=0 svc file pid port pids
  for svc in api web preview; do
    file="$(pid_file "$svc")"
    if [[ -f "$file" ]] && pid="$(cat "$file" 2>/dev/null)" && alive "$pid"; then
      ok "$svc running (pid $pid)"
      anything=1
    fi
  done
  if [[ "$anything" -eq 0 ]]; then
    info "nothing started by this script is running"
  fi

  for port in "$API_PORT" "$WEB_PORT" "$PREVIEW_PORT"; do
    pids="$(listener_pids "$port" | tr '\n' ' ')"
    if [[ -n "${pids// /}" ]]; then
      info "port $port held by pid(s): ${pids% }"
    fi
  done

  if curl -fsS --max-time 2 "http://127.0.0.1:$API_PORT/health" >/dev/null 2>&1; then
    ok "API responding on port $API_PORT"
    curl -fsS --max-time 3 "http://127.0.0.1:$API_PORT/api/v1/health/ready" 2>/dev/null \
      | python3 "$ROOT/scripts/print_readiness.py" || true
  else
    info "API not responding on port $API_PORT"
  fi
}

cmd_doctor() {
  local problems=0 c

  step "Checking prerequisites"
  for c in python3 node npm curl; do
    if command -v "$c" >/dev/null 2>&1; then
      ok "$c $("$c" --version 2>&1 | head -n1 | cut -c1-40)"
    else
      warn "$c is missing"; problems=1
    fi
  done
  if command -v psql >/dev/null 2>&1; then
    ok "psql $(psql --version | awk '{print $3}')"
  else
    warn "psql is missing (sudo apt install postgresql)"; problems=1
  fi

  step "Checking PostgreSQL"
  if command -v pg_isready >/dev/null 2>&1 && pg_isready -q -h 127.0.0.1 2>/dev/null; then
    ok "accepting connections on 127.0.0.1:5432"
  else
    warn "not reachable — try: sudo systemctl start postgresql"; problems=1
  fi
  if db_reachable; then
    ok "can connect to $DB_NAME as $DB_USER"
  else
    warn "cannot connect as $DB_USER — run: ./run.sh db"; problems=1
  fi

  step "Checking project state"
  if [[ -x "$PY" ]]; then ok "backend venv present"; else warn "no backend venv — run ./run.sh setup"; problems=1; fi
  if [[ -d "$FRONTEND/node_modules" ]]; then ok "frontend dependencies installed"; else warn "no node_modules — run ./run.sh setup"; problems=1; fi
  if [[ -f "$BACKEND/.env" ]]; then ok "backend/.env present"; else warn "no backend/.env — run ./run.sh setup"; problems=1; fi
  if [[ -f "$FRONTEND/.env" ]]; then ok "frontend/.env present"; else warn "no frontend/.env (created on next run)"; fi
  if [[ -f "$BACKEND/content/manifest.json" ]]; then
    local modules
    modules="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["modules"]))' \
      "$BACKEND/content/manifest.json" 2>/dev/null || echo '?')"
    ok "content manifest present ($modules modules)"
  else
    warn "no content manifest — run ./run.sh manifest"; problems=1
  fi

  step "Checking ports"
  local pair name port
  for pair in "api:$API_PORT" "web:$WEB_PORT" "preview:$PREVIEW_PORT"; do
    name="${pair%%:*}"; port="${pair##*:}"
    if port_busy "$port"; then
      warn "$name port $port is in use (./run.sh stop will release it)"
    else
      ok "$name port $port is free"
    fi
  done

  printf '\n'
  if [[ "$problems" -eq 0 ]]; then
    ok "No problems found."
  else
    warn "See the notes above."
  fi
}

usage() {
  # Print the leading comment block (skipping the shebang) as the help text.
  awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 && !/^#/ { exit }' "${BASH_SOURCE[0]}"
}

case "${1:-dev}" in
  dev|"")         cmd_dev ;;
  setup)          cmd_setup ;;
  db)             cmd_db ;;
  reset-db)       cmd_reset_db ;;
  migrate)        cmd_migrate ;;
  seed)           cmd_seed ;;
  manifest)       cmd_manifest ;;
  test)           cmd_test ;;
  e2e)            cmd_e2e ;;
  build)          cmd_build ;;
  preview)        cmd_preview ;;
  stop)           cmd_stop ;;
  status)         cmd_status ;;
  logs)           cmd_logs ;;
  doctor)         cmd_doctor ;;
  -h|--help|help) usage ;;
  *)              printf '%sunknown command: %s%s\n\n' "$RED" "$1" "$R" >&2; usage; exit 2 ;;
esac
