#!/usr/bin/env sh
set -eu

echo "[api] APP_ENV=${APP_ENV:-dev}"
if [ -n "${DATABASE_URL:-}" ]; then
  echo "[api] DATABASE_URL=<set>"
else
  echo "[api] DATABASE_URL=<empty>"
fi

# 1) Sync deps at startup (uses uv.lock)
echo "[api] uv sync (startup)"
uv sync

# 2) Run migrations
echo "[api] alembic upgrade head"
uv run alembic upgrade head

# 3) Start uvicorn in background (reload for code changes)
echo "[api] starting uvicorn (reload)"
uv run uvicorn app.main:app \
  --host 0.0.0.0 --port 8000 \
  --reload --reload-dir /app/app \
  &
UVICORN_PID="$!"

# 4) Watch lock + pyproject; on change, resync + restart uvicorn
echo "[api] watching uv.lock / pyproject.toml for dependency changes"

# Uses watchfiles CLI (install it as a dev dependency if not present)
# On change: uv sync && restart uvicorn process
uv run watchfiles --filter python "
sh -lc '
  echo \"[api] deps changed -> uv sync\";
  uv sync;
  echo \"[api] restarting uvicorn\";
  uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/app'
" /app/uv.lock /app/pyproject.toml /app/app
