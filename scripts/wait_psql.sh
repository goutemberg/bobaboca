#!/usr/bin/env sh
set -e

HOST="${1:-${POSTGRES_HOST:-psql}}"
PORT="${2:-${POSTGRES_PORT:-5432}}"
TIMEOUT="${3:-60}"

echo "Waiting for Postgres at ${HOST}:${PORT} (timeout ${TIMEOUT}s)…"

i=0
while [ $i -lt "$TIMEOUT" ]; do
  if python - <<PY
import socket, sys
host = "${HOST}"
port = int("${PORT}")
s = socket.socket()
s.settimeout(1)
try:
    s.connect((host, port))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  then
    echo "Postgres is up."
    exit 0
  fi
  i=$((i+1))
  sleep 1
done

echo "Timed out waiting for Postgres ${HOST}:${PORT}"
exit 1
