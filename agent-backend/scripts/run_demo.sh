#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

printf '启动 XERP Demo：http://%s:%s/demo\n' "$HOST" "$PORT"
exec uv run uvicorn app.main:app --host "$HOST" --port "$PORT"
