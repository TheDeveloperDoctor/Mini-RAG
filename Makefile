.PHONY: help install install-api install-web dev dev-api dev-web test test-api test-web lint typecheck eval seed docker-build docker-up docker-down clean

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
help:
	@echo "Mini RAG — make targets"
	@echo ""
	@echo "  install         Install API + web deps"
	@echo "  dev             Run API + web concurrently"
	@echo "  test            Run all tests"
	@echo "  lint            Lint API + web"
	@echo "  typecheck       Type-check API + web"
	@echo "  eval            Run eval harness, write results to eval_results/"
	@echo "  seed            Seed corpus (Paul Graham essays) into the API"
	@echo "  docker-build    Build all docker images"
	@echo "  docker-up       Bring stack up (detached)"
	@echo "  docker-down     Tear stack down"
	@echo "  clean           Remove build artifacts, caches, and data"

# ------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------
install: install-api install-web

install-api:
	cd apps/api && python3 -m venv .venv && . .venv/bin/activate && \
		pip install -U pip && pip install -e ".[dev]"

install-web:
	cd apps/web && pnpm install

# ------------------------------------------------------------------------------
# Dev
# ------------------------------------------------------------------------------
dev:
	@echo "Run 'make dev-api' and 'make dev-web' in separate terminals,"
	@echo "or use 'make docker-up' for the full stack."

dev-api:
	cd apps/api && . .venv/bin/activate && \
		uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

dev-web:
	cd apps/web && pnpm dev

# ------------------------------------------------------------------------------
# Test / Lint / Typecheck
# ------------------------------------------------------------------------------
test: test-api test-web

test-api:
	cd apps/api && . .venv/bin/activate && pytest -q

test-web:
	cd apps/web && pnpm test --run || true

lint:
	cd apps/api && . .venv/bin/activate && ruff check src tests
	cd apps/web && pnpm lint

typecheck:
	cd apps/api && . .venv/bin/activate && mypy src
	cd apps/web && pnpm typecheck

# ------------------------------------------------------------------------------
# Eval
# ------------------------------------------------------------------------------
eval:
	cd apps/api && . .venv/bin/activate && python -m src.eval.harness

seed:
	cd apps/api && . .venv/bin/activate && python -m src.scripts.seed_pg_essays

# ------------------------------------------------------------------------------
# Docker
# ------------------------------------------------------------------------------
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

# ------------------------------------------------------------------------------
# Clean
# ------------------------------------------------------------------------------
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name ".next" -prune -exec rm -rf {} +
	find . -type d -name "node_modules" -prune -exec rm -rf {} +
	rm -rf apps/api/.venv apps/api/data apps/api/.hf_cache eval_results/*.json
