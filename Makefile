# ─────────────────────────────────────────────
# Platform Backend — Makefile
# Usage: make <target>
# ─────────────────────────────────────────────

.PHONY: help install run migrate migrations test lint format shell createsuperuser \
        docker-dev docker-staging docker-prod docker-build celery beat logs clean

PYTHON      = python
MANAGE      = $(PYTHON) manage.py
DOCKER_DEV  = docker-compose -f docker/docker-compose.yml
DOCKER_STAG = docker-compose -f docker/docker-compose.staging.yml
DOCKER_PROD = docker-compose -f docker/docker-compose.prod.yml

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ── Local Development ──────────────────────────────────────
install:  ## Install dependencies (development)
	pip install -r requirements/development.txt

run:  ## Start Django dev server
	DJANGO_ENV=development $(MANAGE) runserver 0.0.0.0:8000

migrate:  ## Apply all migrations
	$(MANAGE) migrate

migrations:  ## Create new migrations (pass app= to target specific app)
	$(MANAGE) makemigrations $(app)

seed:  ## Seed system config defaults
	$(MANAGE) seed_system_config

shell:  ## Open Django shell
	$(MANAGE) shell_plus 2>/dev/null || $(MANAGE) shell

createsuperuser:  ## Create ROOT user via CLI script
	$(PYTHON) scripts/create_root_user.py

collectstatic:  ## Collect static files
	$(MANAGE) collectstatic --noinput

# ── Testing ────────────────────────────────────────────────
test:  ## Run all tests
	DJANGO_ENV=test pytest

test-fast:  ## Run tests without coverage
	DJANGO_ENV=test pytest --no-cov -x

test-app:  ## Run tests for a specific app (make test-app app=users)
	DJANGO_ENV=test pytest apps/$(app)/tests/ -v

# ── Code Quality ───────────────────────────────────────────
lint:  ## Run flake8 linter
	flake8 apps/ config/

format:  ## Format code with black + isort
	black apps/ config/ scripts/
	isort apps/ config/ scripts/

typecheck:  ## Run mypy type checks
	mypy apps/ config/

# ── Docker — Development ───────────────────────────────────
docker-dev:  ## Start dev stack (Django + Postgres + Redis)
	$(DOCKER_DEV) up

docker-dev-build:  ## Rebuild and start dev stack
	$(DOCKER_DEV) up --build

docker-dev-down:  ## Stop dev stack
	$(DOCKER_DEV) down

# ── Docker — Staging ───────────────────────────────────────
docker-staging:  ## Start staging stack
	$(DOCKER_STAG) up -d

docker-staging-down:  ## Stop staging stack
	$(DOCKER_STAG) down

# ── Docker — Production ────────────────────────────────────
docker-build:  ## Build production Docker image
	docker build -f docker/Dockerfile -t platform-api:latest .

docker-prod:  ## Start production stack
	$(DOCKER_PROD) up -d --remove-orphans

docker-prod-down:  ## Stop production stack
	$(DOCKER_PROD) down

docker-prod-logs:  ## Tail production logs
	$(DOCKER_PROD) logs -f api

# ── Celery ────────────────────────────────────────────────
celery:  ## Start Celery worker (development)
	DJANGO_ENV=development celery -A config worker -l info

beat:  ## Start Celery Beat scheduler (development)
	DJANGO_ENV=development celery -A config beat -l info

# ── Utilities ─────────────────────────────────────────────
logs:  ## Tail Django logs
	tail -f /var/log/platform/django.log

clean:  ## Remove __pycache__, .pyc files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null; true

backup-db:  ## Backup production database
	$(DOCKER_PROD) exec db pg_dump -U $$DB_USER $$DB_NAME > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db:  ## Restore database (make restore-db file=backup.sql)
	$(DOCKER_PROD) exec -T db psql -U $$DB_USER $$DB_NAME < $(file)
