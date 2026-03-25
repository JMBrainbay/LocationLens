#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-fixture}"
START_FLAG="${2:-}"

if [[ "$MODE" != "fixture" && "$MODE" != "live" ]]; then
  echo "Usage: ./scripts/workshop-reset.sh [fixture|live] [--no-start]"
  exit 1
fi

if [[ "$START_FLAG" != "" && "$START_FLAG" != "--no-start" ]]; then
  echo "Usage: ./scripts/workshop-reset.sh [fixture|live] [--no-start]"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_EXAMPLE="$ROOT_DIR/.env.example"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_EXAMPLE" ]]; then
  echo "Missing .env.example at $ENV_EXAMPLE"
  exit 1
fi

awk -v mode="$MODE" '
  BEGIN {
    location = mode == "live" ? "live" : "fixture"
    building = mode == "live" ? "live" : "fixture"
    metrics = mode == "live" ? "live" : "fixture"
  }
  /^LOCATION_PROVIDER=/ { print "LOCATION_PROVIDER=" location; next }
  /^BUILDING_PROVIDER=/ { print "BUILDING_PROVIDER=" building; next }
  /^METRICS_PROVIDER=/ { print "METRICS_PROVIDER=" metrics; next }
  { print }
' "$ENV_EXAMPLE" > "$ENV_FILE"

echo "Wrote clean .env in ${MODE} mode."

pkill -f "uvicorn src.app:app" >/dev/null 2>&1 || true
pkill -f "next dev -p 3000" >/dev/null 2>&1 || true
echo "Stopped old dev processes (if running)."

cd "$ROOT_DIR"
corepack pnpm install >/dev/null
echo "Ensured pnpm dependencies are installed."

if ! python3 -c "import fastapi, httpx, pydantic, pydantic_settings, pytest, mypy, uvicorn, eval_type_backport" >/dev/null 2>&1; then
  echo "Installing missing Python dependencies..."
  python3 -m pip install fastapi httpx pydantic pydantic-settings pytest mypy uvicorn eval_type_backport >/dev/null
fi

if [[ "$START_FLAG" == "--no-start" ]]; then
  echo "Reset complete. Start manually with: corepack pnpm dev"
  exit 0
fi

echo "Starting API and web..."
corepack pnpm dev
