#!/usr/bin/env bash
# run.sh — trigger the full pipeline
# Checks that Airbyte is reachable, then runs the Dagster job.
# Docker Desktop and Airbyte must already be running (abctl local install).

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[run]${NC}   $1"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $1"; }
error() { echo -e "${RED}[error]${NC} $1"; exit 1; }

# Load env

if [ ! -f .env ]; then
    error ".env file not found."
fi

export $(grep -v '^#' .env | grep -v '^$' | xargs)

# ── Check Airbyte is reachable ────────────────────────────────────────────────

AIRBYTE_URL="http://${AIRBYTE_HOST:-localhost}:${AIRBYTE_PORT:-8000}"

info "Checking Airbyte at $AIRBYTE_URL..."

if ! curl -s --max-time 5 "$AIRBYTE_URL" > /dev/null 2>&1; then
    error "Airbyte is not reachable at $AIRBYTE_URL. Start it with: abctl local start"
fi

info "Airbyte is up."

# Check AIRBYTE_CONNECTION_ID is set

if [ -z "${AIRBYTE_CONNECTION_ID:-}" ] || [ "$AIRBYTE_CONNECTION_ID" = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" ]; then
    error "AIRBYTE_CONNECTION_ID is not set in .env. Configure the connection in Airbyte UI first."
fi

# Run the Dagster pipeline

info "Running job_market_pipeline_job..."
echo ""

dagster job execute \
    --module-name dagsters.definitions \
    --job job_market_pipeline_job

echo ""
info "Pipeline run complete."
