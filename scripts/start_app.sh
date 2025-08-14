#!/usr/bin/env sh
set -e

# 🔒 Normaliza porta (se não setada ou vazia, vira 8000)
PORT="${PORT:-8000}"
case "$PORT" in
  ''|*[!0-9]*)
    echo ">> PORT inválido ('$PORT'), usando 8000"
    PORT=8000
    ;;
esac

VENV_PY="/venv/bin/python"

echo "==> DEBUG=${DEBUG:-}"
echo "==> DATABASE_URL present? $( [ -n "$DATABASE_URL" ] && echo yes || echo no )"
echo "==> POSTGRES_HOST=${POSTGRES_HOST:-<none>} POSTGRES_PORT=${POSTGRES_PORT:-<none>}"

# DEV: se DEBUG=true e tiver POSTGRES_*, ignora DATABASE_URL
if [ "${DEBUG:-false}" = "true" ] && [ -n "${POSTGRES_HOST:-}" ]; then
  echo "==> DEV: ignorando DATABASE_URL e usando POSTGRES_* locais"
  unset DATABASE_URL
fi

# Descobre host/port do banco para aguardar
get_host_port_from_dburl() {
  $VENV_PY - <<'PY'
import os
from urllib.parse import urlparse
u = os.getenv("DATABASE_URL", "")
p = urlparse(u) if u else None
host = (p.hostname if p else "") or ""
port = (p.port if p else 5432)
print(f"{host}:{port}")
PY
}

if [ -n "${DATABASE_URL:-}" ]; then
  HP="$(get_host_port_from_dburl)"
  DB_HOST="${HP%:*}"
  DB_PORT="${HP#*:}"
else
  DB_HOST="${POSTGRES_HOST:-psql}"
  DB_PORT="${POSTGRES_PORT:-5432}"
fi

echo "==> Aguardando Postgres em ${DB_HOST}:${DB_PORT}…"
/scripts/wait_psql.sh "$DB_HOST" "$DB_PORT" 90

echo "==> collectstatic"
/scripts/collectstatic.sh || true

echo "==> migrate"
/scripts/migrate.sh

# Diagnóstico rápido (opcional)
$VENV_PY -c "import sys; print('>>> python:', sys.executable)"
$VENV_PY -c "import gunicorn, sys; print('>>> gunicorn:', gunicorn.__version__)"

if [ -n "${DATABASE_URL:-}" ] && [ "${DEBUG:-false}" != "true" ]; then
  echo "==> PROD: subindo gunicorn (via python -m)"
  exec $VENV_PY -m gunicorn bocaboca.wsgi:application --bind 0.0.0.0:${PORT:-8000}
else
  echo "==> DEV: subindo runserver (via venv python)"
  exec $VENV_PY manage.py runserver 0.0.0.0:8000
fi
