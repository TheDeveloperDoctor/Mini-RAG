.PHONY: help install install-api install-api-user install-web dev dev-api dev-web \
        test test-api test-web lint typecheck eval seed \
        docker-build docker-up docker-down docker-logs clean \
        precommit-install ci-api ci-web

# ------------------------------------------------------------------------------
# Resolve Python entrypoint: prefer .venv if it exists, else system python3.
# This lets the project work on systems without python3-venv installed.
# ------------------------------------------------------------------------------
VENV_DIR := $(CURDIR)/apps/api/.venv
ifeq ($(wildcard $(VENV_DIR)/bin/python),)
PY      := python3
PIP     := pip3
USE_VENV := 0
else
PY      := $(VENV_DIR)/bin/python
PIP     := $(VENV_DIR)/bin/pip
USE_VENV := 1
endif

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
help:
	@echo "Mini RAG — make targets"
	@echo ""
	@echo "  install              Install API (venv) + web deps"
	@echo "  install-api          Install API into .venv (needs python3-venv)"
	@echo "  install-api-user     Install API system-wide via pip --user (no venv)"
	@echo "  install-web          Install web deps via pnpm"
	@echo ""
	@echo "  dev-api              Run API on :8000 (auto-detects venv)"
	@echo "  dev-web              Run web on :3000"
	@echo ""
	@echo "  test                 Run all tests (API + web)"
	@echo "  lint                 Lint API + web"
	@echo "  typecheck            Type-check API + web"
	@echo ""
	@echo "  eval                 Run eval harness; writes JSON to eval_results/"
	@echo "  seed                 Seed runtime DB with the eval corpus"
	@echo ""
	@echo "  docker-build         Build images"
	@echo "  docker-up            Bring stack up (detached)"
	@echo "  docker-logs          Tail compose logs"
	@echo "  docker-down          Tear stack down"
	@echo ""
	@echo "  precommit-install    Install pre-commit hooks"
	@echo "  clean                Remove build artifacts, caches, and data"

# ------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------
install: install-api install-web

install-api:
	@if ! python3 -c 'import ensurepip' >/dev/null 2>&1; then \
		echo ""; \
		echo "  python3-venv is not installed. Two options:"; \
		echo ""; \
		echo "    1. Install it:   sudo apt install python3-venv"; \
		echo "       then re-run:  make install-api"; \
		echo ""; \
		echo "    2. Skip venv:    make install-api-user"; \
		echo "       (uses pip --user --break-system-packages)"; \
		echo ""; \
		exit 1; \
	fi
	cd apps/api && python3 -m venv .venv && \
		./.venv/bin/pip install -U pip && \
		./.venv/bin/pip install -e ".[dev]"

install-api-user:
	cd apps/api && pip3 install --user --break-system-packages -U pip && \
		pip3 install --user --break-system-packages -e ".[dev]"

install-web:
	cd apps/web && pnpm install

# ------------------------------------------------------------------------------
# Dev
# ------------------------------------------------------------------------------
dev-api:
	cd apps/api && PYTHONPATH=. $(PY) -m uvicorn src.main:app \
		--host 0.0.0.0 --port 8000 --reload
ifeq ($(USE_VENV),0)
	@echo "(running with system python3 — set up venv via 'make install-api' if you prefer)"
endif

dev-web:
	cd apps/web && pnpm dev

# ------------------------------------------------------------------------------
# Test / Lint / Typecheck
# ------------------------------------------------------------------------------
test: test-api test-web

test-api:
	cd apps/api && PYTHONPATH=. $(PY) -m pytest -q

test-web:
	cd apps/web && pnpm test --run || true

lint:
	cd apps/api && PYTHONPATH=. $(PY) -m ruff check src tests
	cd apps/web && pnpm lint

typecheck:
	cd apps/api && PYTHONPATH=. $(PY) -m mypy src
	cd apps/web && pnpm typecheck

# CI targets — fail fast, no fallback noise.
ci-api: lint typecheck test-api
ci-web:
	cd apps/web && pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm build

# ------------------------------------------------------------------------------
# Eval / Seed
# ------------------------------------------------------------------------------
eval:
	cd apps/api && PYTHONPATH=. $(PY) -m src.eval.harness

seed:
	cd apps/api && PYTHONPATH=. $(PY) -m src.scripts.seed_pg_essays

# ------------------------------------------------------------------------------
# Docker
# ------------------------------------------------------------------------------
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-logs:
	docker compose logs -f --tail=200

docker-down:
	docker compose down

# ------------------------------------------------------------------------------
# Pre-commit
# ------------------------------------------------------------------------------
precommit-install:
	$(PIP) install --user --break-system-packages pre-commit || $(PIP) install pre-commit
	pre-commit install

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
