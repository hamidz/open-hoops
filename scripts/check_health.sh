#!/usr/bin/env bash
# Open Hoops — Health Check Script
#
# Checks all services are reachable and healthy.
# Usage:
#   ./scripts/check_health.sh          # Verbose output
#   ./scripts/check_health.sh --quiet  # Silent, exit code only

set -euo pipefail

QUIET=false
[[ "${1:-}" == "--quiet" ]] && QUIET=true

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    local expected="${3:-}"

    if output=$(eval "$cmd" 2>&1); then
        if [[ -n "$expected" && "$output" != *"$expected"* ]]; then
            [[ "$QUIET" == "false" ]] && echo -e "  ${RED}✗${NC} $name — unexpected response"
            FAIL=$((FAIL + 1))
        else
            [[ "$QUIET" == "false" ]] && echo -e "  ${GREEN}✓${NC} $name"
            PASS=$((PASS + 1))
        fi
    else
        [[ "$QUIET" == "false" ]] && echo -e "  ${RED}✗${NC} $name — not reachable"
        FAIL=$((FAIL + 1))
    fi
}

[[ "$QUIET" == "false" ]] && echo "" && echo "Open Hoops — Health Check" && echo ""

# API health endpoint (checks postgres, redis, minio, ollama internally)
check "API (FastAPI)"           'curl -sf http://localhost:8000/api/v1/health' '"status":"ok"'
check "Frontend (Next.js)"      'curl -sf -o /dev/null -w "%{http_code}" http://localhost:3000' '200'
check "MinIO API"               'curl -sf http://localhost:9000/minio/health/live'
check "MinIO Console"           'curl -sf -o /dev/null -w "%{http_code}" http://localhost:9001' '200'
check "Ollama"                  'curl -sf http://localhost:11434/api/tags' '"models"'
check "PostgreSQL (via Docker)" 'docker compose -f infra/docker-compose.yml exec -T postgres pg_isready -U openhoops 2>&1'
check "Redis (via Docker)"      'docker compose -f infra/docker-compose.yml exec -T redis redis-cli ping' 'PONG'

[[ "$QUIET" == "false" ]] && echo ""

if [[ $FAIL -eq 0 ]]; then
    [[ "$QUIET" == "false" ]] && echo -e "${GREEN}All ${PASS} checks passed.${NC}"
    exit 0
else
    [[ "$QUIET" == "false" ]] && echo -e "${RED}${FAIL} check(s) failed. ${PASS} passed.${NC}"
    [[ "$QUIET" == "false" ]] && echo "" && echo "Troubleshoot: docker compose -f infra/docker-compose.yml logs <service>"
    exit 1
fi
