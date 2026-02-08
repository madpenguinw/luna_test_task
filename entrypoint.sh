#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('${APP_POSTGRES_DATA_HOST:-db}', ${APP_POSTGRES_DATA_PORT:-5432}))
    s.close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Running migrations..."
uv run alembic upgrade head

echo "Seeding database..."
uv run python -m src.seed

echo "Starting application..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
