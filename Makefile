# Open Hoops — Makefile
#
# Run these commands from the repository root (inside WSL2 on Windows).
#
# Usage:
#   make dev          Start the local dev stack
#   make dev-gpu      Start with AMD ROCm GPU acceleration
#   make stop         Stop all containers
#   make logs         Tail all container logs
#   make health       Check all service health
#   make lint         Run all linters (Python + TypeScript)
#   make test         Run all test suites
#   make build        Build all Docker images
#   make generate-types  Regenerate TypeScript types from Pydantic models
#   make seed         Seed mock data into local stack
#   make clean        Remove containers and volumes (DESTRUCTIVE)

.PHONY: dev dev-gpu stop logs health lint lint-python lint-frontend test test-python test-frontend test-visual build generate-types seed clean help

COMPOSE      = docker compose -f infra/docker-compose.yml
COMPOSE_GPU  = $(COMPOSE) -f infra/docker-compose.gpu.yml
COMPOSE_PROD = $(COMPOSE) -f infra/docker-compose.prod.yml

# ─────────────────────────────────────────────
# Stack Management
# ─────────────────────────────────────────────

dev:
	@echo "Starting Open Hoops dev stack (CPU mode)..."
	@test -f .env || (echo "ERROR: .env not found. Run: cp .env.example .env" && exit 1)
	$(COMPOSE) up -d
	@echo "Stack running. Dashboard: http://localhost:3000"

dev-gpu:
	@echo "Starting Open Hoops dev stack (AMD ROCm GPU mode)..."
	@test -f .env || (echo "ERROR: .env not found. Run: cp .env.example .env" && exit 1)
	$(COMPOSE_GPU) up -d
	@echo "Stack running with ROCm GPU. Dashboard: http://localhost:3000"

stop:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

health:
	@./scripts/check_health.sh

# ─────────────────────────────────────────────
# Linting
# ─────────────────────────────────────────────

lint: lint-python lint-frontend

lint-python:
	@echo "Linting Python..."
	ruff check apps/api/ services/
	ruff format --check apps/api/ services/
	mypy apps/api/app/ services/cv_worker/ services/analytics_worker/ services/llm_service/ --exclude tests

lint-frontend:
	@echo "Linting TypeScript/Next.js..."
	npm run lint --workspace web
	npm exec --workspace web -- tsc --noEmit

# ─────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────

test: test-python test-frontend

test-python:
	@echo "Running Python tests..."
	pytest apps/api/tests/ -v --cov=app --cov-report=term-missing
	pytest services/cv_worker/tests/ -v --cov=pipeline --cov-report=term-missing
	pytest services/analytics_worker/tests/ -v --cov=analytics --cov-report=term-missing
	pytest services/llm_service/tests/ -v --cov=llm --cov-report=term-missing

test-frontend:
	@echo "Running frontend tests..."
	npm test --workspace web -- --run

test-visual:
	@echo "Running Playwright visual regression tests (requires running dev stack)..."
	npm exec --workspace web -- playwright test

# ─────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────

build:
	@echo "Building all Docker images..."
	$(COMPOSE) build

build-prod:
	$(COMPOSE_PROD) build

# ─────────────────────────────────────────────
# Type Generation
# ─────────────────────────────────────────────

generate-types:
	@echo "Generating TypeScript types from Pydantic models..."
	cd packages/shared_types && python generate_types.py
	@echo "Types written to packages/shared_types/types/"
	@echo "Check for uncommitted changes: git diff packages/shared_types/types/"

# CI check: fails if generated types differ from committed types
check-types-sync:
	$(MAKE) generate-types
	@git diff --exit-code packages/shared_types/types/ || \
		(echo "ERROR: TypeScript types are out of sync. Run 'make generate-types' and commit the changes." && exit 1)
	@echo "TypeScript types are in sync."

# ─────────────────────────────────────────────
# Development Helpers
# ─────────────────────────────────────────────

seed:
	@echo "Seeding mock data..."
	python scripts/generate_mock_data.py

setup:
	@./scripts/setup.sh

clean:
	@echo "WARNING: This will remove all containers AND volumes (all data will be lost)."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(COMPOSE) down -v
	@echo "Containers and volumes removed."

# ─────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────

help:
	@echo ""
	@echo "Open Hoops Makefile Commands:"
	@echo ""
	@echo "  make dev             Start dev stack (CPU)"
	@echo "  make dev-gpu         Start dev stack (AMD ROCm GPU)"
	@echo "  make stop            Stop all containers"
	@echo "  make logs            Tail all container logs"
	@echo "  make health          Check service health"
	@echo ""
	@echo "  make lint            Run all linters"
	@echo "  make test            Run all tests"
	@echo "  make test-visual     Run visual regression tests (dev stack required)"
	@echo "  make build           Build all Docker images"
	@echo ""
	@echo "  make generate-types  Regenerate TypeScript types from Pydantic models"
	@echo "  make check-types-sync Verify types are in sync (CI gate)"
	@echo "  make seed            Seed mock data"
	@echo "  make setup           Run first-time setup"
	@echo "  make clean           Remove containers and volumes (DESTRUCTIVE)"
	@echo ""
