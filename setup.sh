#!/usr/bin/env bash
# setup.sh — one-time project setup
# Run this once to provision infrastructure and install dependencies.
# After this script, configure the Airbyte connector manually (see step 4).

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[setup]${NC} $1"; }
warn()    { echo -e "${YELLOW}[warn]${NC}  $1"; }
error()   { echo -e "${RED}[error]${NC} $1"; exit 1; }

#1. Check prerequisites

info "Checking prerequisites..."

command -v terraform >/dev/null 2>&1 || error "terraform not found. Install from https://developer.hashicorp.com/terraform/install"
command -v abctl     >/dev/null 2>&1 || error "abctl not found. Run: brew install airbytehq/tap/abctl"
command -v python3   >/dev/null 2>&1 || error "python3 not found."
command -v pip       >/dev/null 2>&1 || error "pip not found."

if [ ! -f .env ]; then
    error ".env file not found. Copy .env.example to .env and fill in your values."
fi

info "All prerequisites met."

# Load .env so TF_VAR_* are available to Terraform
export $(grep -v '^#' .env | grep -v '^$' | xargs)
export TF_VAR_gcp_credentials_path="$GOOGLE_APPLICATION_CREDENTIALS"

#2. Terraform — provision BigQuery

info "Initialising Terraform..."
terraform -chdir=terraform init -upgrade

info "Applying Terraform (BigQuery dataset + table)...)"
terraform -chdir=terraform apply -auto-approve

#3. Python dependencies

info "Installing Python dependencies..."
pip install -e . --quiet

#4. Airbyte

info "Starting Airbyte (this takes a few minutes on first run)..."
abctl local install

echo ""
warn "Airbyte is running at http://localhost:8000"
warn "Complete the following steps manually before running run.sh:"
echo ""
echo "  1. Log in with credentials from: abctl local credentials"
echo "  2. Sources → New Source → Custom connector → paste airbyte/bundesagentur_source.yaml"
echo "  3. Destinations → New Destination → BigQuery → use your service account JSON"
echo "  4. Connections → New Connection → link the source and destination"
echo "  5. Copy the connection UUID from the URL and set it in .env as AIRBYTE_CONNECTION_ID"
echo ""

info "Setup complete. Run ./run.sh once Airbyte is configured."
