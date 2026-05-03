#!/usr/bin/env bash
# Open Hoops — First-Time Setup Script
#
# This script:
#   1. Checks prerequisites
#   2. Copies .env.example to .env (if not present)
#   3. Validates that required variables are filled
#   4. Starts the Docker stack
#   5. Waits for services to be healthy
#   6. Creates MinIO buckets (via minio-init container)
#   7. Pulls the default Ollama LLM model
#
# Usage: ./scripts/setup.sh

set -euo pipefail

# ─────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()    { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ─────────────────────────────────────────────
# Change to repo root
# ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo ""
echo "╔═══════════════════════════════════╗"
echo "║     Open Hoops — Setup Script     ║"
echo "╚═══════════════════════════════════╝"
echo ""

# ─────────────────────────────────────────────
# 1. Check Prerequisites
# ─────────────────────────────────────────────
info "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || error "Docker is not installed or not in PATH. Install Docker Desktop with WSL2 backend."
command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 || error "Docker Compose v2 is required. Update Docker Desktop."

DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
info "Docker version: ${DOCKER_VERSION}"

# Warn if running on Windows filesystem (not WSL2 Linux filesystem)
if [[ "$(pwd)" == /mnt/* ]]; then
    warn "You are running from a Windows filesystem mount (${REPO_ROOT})."
    warn "For best performance, clone the repo inside WSL2's Linux filesystem: ~/open-hoops"
    warn "See CONTRIBUTING.md for details."
fi

# ─────────────────────────────────────────────
# 2. Copy .env if not present
# ─────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
    info "No .env file found. Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    warn "IMPORTANT: Edit .env before continuing."
    warn "At minimum, set:"
    warn "  POSTGRES_PASSWORD=<strong password>"
    warn "  MINIO_ROOT_PASSWORD=<strong password (min 8 chars)>"
    echo ""
    read -p "Press Enter when you have edited .env to continue, or Ctrl+C to exit..."
else
    info ".env file found."
fi

# ─────────────────────────────────────────────
# 3. Validate required env vars
# ─────────────────────────────────────────────
info "Validating .env..."

# shellcheck source=/dev/null
source .env

[[ "${POSTGRES_PASSWORD:-changeme_use_a_strong_password}" == "changeme_use_a_strong_password" ]] && \
    error "POSTGRES_PASSWORD is still the default placeholder. Edit .env and set a real password."

[[ "${MINIO_ROOT_PASSWORD:-changeme_minio_password}" == "changeme_minio_password" ]] && \
    error "MINIO_ROOT_PASSWORD is still the default placeholder. Edit .env and set a real password."

info "Environment variables look OK."

# ─────────────────────────────────────────────
# 4. Start the stack
# ─────────────────────────────────────────────
info "Starting Docker Compose stack..."
docker compose --env-file .env -f infra/docker-compose.yml up -d --build

# ─────────────────────────────────────────────
# 5. Wait for health
# ─────────────────────────────────────────────
info "Waiting for services to become healthy (up to 2 minutes)..."
sleep 10

MAX_WAIT=120
ELAPSED=0
while ! ./scripts/check_health.sh --quiet 2>/dev/null; do
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    if [[ $ELAPSED -ge $MAX_WAIT ]]; then
        warn "Services did not become healthy within ${MAX_WAIT}s."
        warn "Check logs: docker compose --env-file .env -f infra/docker-compose.yml logs"
        break
    fi
    echo -n "."
done
echo ""

# ─────────────────────────────────────────────
# 6. Pull Ollama model
# ─────────────────────────────────────────────
LLM_MODEL="${LLM_MODEL:-llama3.1:8b}"
info "Pulling Ollama model: ${LLM_MODEL}"
info "(This may take several minutes on first run — ${LLM_MODEL} is ~4–5 GB)"
docker compose --env-file .env -f infra/docker-compose.yml exec ollama ollama pull "${LLM_MODEL}" || \
    warn "Ollama model pull failed. You can pull it manually: docker compose --env-file .env -f infra/docker-compose.yml exec ollama ollama pull ${LLM_MODEL}"

# ─────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────
echo ""
info "Setup complete!"
echo ""
echo "  Dashboard:     http://localhost:${WEB_PORT:-3000}"
echo "  API:           http://localhost:${API_PORT:-8000}/api/v1/health"
echo "  API Docs:      http://localhost:${API_PORT:-8000}/docs"
echo "  MinIO Console: http://localhost:${MINIO_CONSOLE_PORT:-9001}"
echo ""
echo "  Stop stack:   make stop"
echo "  View logs:    make logs"
echo "  Run tests:    make test"
echo ""
