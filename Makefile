.PHONY: install run test lint fmt typecheck check up down

install:   ## Install all dependencies
	uv sync

run:       ## Start the API with auto-reload
	uv run provena

test:      ## Run tests with coverage
	uv run pytest --cov

lint:      ## Lint and check formatting
	uv run ruff check .
	uv run ruff format --check .

fmt:       ## Auto-fix lint and formatting
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Strict type checking
	uv run mypy src tests

check: lint typecheck test  ## Everything CI runs

up:        ## Start API + Qdrant in Docker
	docker compose up --build -d

down:
	docker compose down
