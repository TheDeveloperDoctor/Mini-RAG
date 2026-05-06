.PHONY: help install install-api install-web bootstrap-uv \
        dev-api dev-web \
        test test-api test-web lint typecheck eval seed \
        docker-build docker-up docker-down docker-logs clean \
        precommit-install ci-api ci-web

# ------------------------------------------------------------------------------
# All Python work goes through `uv` — it manages the venv, lockfile, and
# Python interpreter. No 'python3-venv' system package required.
# Targets that run Python use `uv run`, which executes inside apps/api/.venv
# (created on `make install-api`).
# ------------------------------------------------------------------------------
UV_RUN_API := cd apps/api && uv run

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
help:
	@echo "Mini RAG — make targets"
	@echo ""
	@echo "  bootstrap-uv         Install uv (curl | sh)"
	@echo "  install              Install API (uv sync) + web (pnpm)"
	@echo "  install-api          uv sync --all-extras inside apps/api"
	@echo "  install-web          pnpm install inside apps/web"
	@echo ""
	@echo "  dev-api              Run API on :8000 via uv"
	@echo "  dev-web              Run web on :3000 via pnpm"
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
# Bootstrap
# ------------------------------------------------------------------------------
bootstrap-uv:
	@if command -v uv >/dev/null 2>&1; then \
		echo "uv already installed: $$(uv --version)"; \
	else \
		echo "Installing uv via official script…"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo ""; \
		echo "uv installed. Open a new shell or run: source \$$HOME/.local/bin/env"; \
	fi

# ------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------
install: install-api install-web

install-api:
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv is not installed. Run 'make bootstrap-uv' first."; \
		exit 1; \
	}
	cd apps/api && uv sync --all-extras

install-web:
	cd apps/web && pnpm install

# ------------------------------------------------------------------------------
# Dev
# ------------------------------------------------------------------------------
dev-api:
	$(UV_RUN_API) uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

dev-web:
	cd apps/web && pnpm dev

# ------------------------------------------------------------------------------
# Test / Lint / Typecheck
# ------------------------------------------------------------------------------
test: test-api test-web

test-api:
	$(UV_RUN_API) pytest -q

test-web:
	cd apps/web && pnpm test --run || true

lint:
	$(UV_RUN_API) ruff check src tests
	cd apps/web && pnpm lint

typecheck:
	$(UV_RUN_API) mypy src
	cd apps/web && pnpm typecheck

ci-api: lint typecheck test-api
ci-web:
	cd apps/web && pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm build

# ------------------------------------------------------------------------------
# Eval / Seed
# ------------------------------------------------------------------------------
eval:
	$(UV_RUN_API) python -m src.eval.harness

seed:
	$(UV_RUN_API) python -m src.scripts.seed_pg_essays

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
	$(UV_RUN_API) pre-commit install || pip install --user --break-system-packages pre-commit && pre-commit install

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
