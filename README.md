# Platform Backend

A production-ready multi-tenant SaaS skeleton built with Django 4.2 + DRF.  
Covers authentication, JWT, 2FA, RBAC, license management, audit logging, impersonation, and more.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Local Desktop Setup (Ubuntu/Debian — apt)](#3-local-desktop-setup-ubuntudebian)
4. [Local Desktop Setup (CentOS/Rocky/RHEL — yum/dnf)](#4-local-desktop-setup-centosrockyrhel)
5. [Environment Configuration](#5-environment-configuration)
6. [First Run — Database & Initial Data](#6-first-run)
7. [Running the Development Server](#7-running-the-development-server)
8. [Staging Server Setup](#8-staging-server-setup)
9. [Production Server Setup (Ubuntu 22.04 LTS)](#9-production-server-setup-ubuntu-2204)
10. [Production Server Setup (Rocky Linux 9)](#10-production-server-setup-rocky-linux-9)
11. [SSL / HTTPS with Let's Encrypt](#11-ssl--https-with-lets-encrypt)
12. [Systemd Service Management](#12-systemd-service-management)
13. [Redis Setup](#13-redis-setup)
14. [PostgreSQL Setup](#14-postgresql-setup)
15. [Docker — Building & Deploying](#15-docker--building--deploying)
16. [Makefile Quick Reference](#16-makefile-quick-reference)
17. [Creating the ROOT User](#17-creating-the-root-user)
18. [Running Tests](#18-running-tests)
19. [Backup & Restore](#19-backup--restore)
20. [Security Hardening Checklist](#20-security-hardening-checklist)
21. [Troubleshooting](#21-troubleshooting)

---

## 1. Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   Client    │────▶│    Nginx     │────▶│   Gunicorn    │
│ (React/Vue) │     │ (SSL, proxy) │     │ (Django API)  │
└─────────────┘     └──────────────┘     └───────┬───────┘
                                                  │
                          ┌───────────────────────┼────────────────────────┐
                          │                       │                        │
                    ┌─────▼─────┐          ┌─────▼─────┐          ┌──────▼─────┐
                    │ PostgreSQL │          │   Redis   │          │   Celery   │
                    │ (primary  │          │ (cache,   │          │ (async     │
                    │  data)    │          │  sessions,│          │  tasks,    │
                    └───────────┘          │  rate-lim)│          │  schedules)│
                                           └───────────┘          └────────────┘
```

**Deployment modes** (set via `DEPLOYMENT_MODE` env var):
- `saas` — your shared server, multiple organisations, ROOT = you
- `self_hosted` — client's dedicated server, single org, ROOT = client

---

## 2. Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| PostgreSQL | 15+ | Primary database |
| Redis | 7+ | Cache, rate limiting, Celery broker |
| Docker | 24+ | Optional but recommended for prod |
| Docker Compose | v2.20+ | Container orchestration |
| Nginx | 1.24+ | Reverse proxy (production) |

---

## 3. Local Desktop Setup (Ubuntu/Debian)

### 3.1 — Install system packages

```bash
sudo apt update && sudo apt upgrade -y

# Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-client-16 libpq-dev

# Redis 7
sudo apt install -y redis-server

# Build tools (needed for some Python packages)
sudo apt install -y build-essential gcc git curl
```

### 3.2 — Start services

```bash
# PostgreSQL
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify both are running
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### 3.3 — Create the database

```bash
# Switch to postgres user
sudo -u postgres psql

-- Inside psql:
CREATE DATABASE platform_dev;
CREATE USER platform_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE platform_dev TO platform_user;
ALTER DATABASE platform_dev OWNER TO platform_user;
\q
```

### 3.4 — Clone and set up the project

```bash
git clone <your-repo-url> platform-backend
cd platform-backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/development.txt
```

---

## 4. Local Desktop Setup (CentOS/Rocky/RHEL)

### 4.1 — Install system packages

```bash
# Update system
sudo dnf update -y

# Enable EPEL and PowerTools (Rocky/AlmaLinux)
sudo dnf install -y epel-release
sudo dnf config-manager --set-enabled crb  # Rocky 9
# OR for CentOS Stream:
# sudo dnf config-manager --set-enabled powertools

# Python 3.12
sudo dnf install -y python3.12 python3.12-devel python3-pip

# PostgreSQL 16
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -qy module disable postgresql
sudo dnf install -y postgresql16-server postgresql16-contrib postgresql16-devel
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
sudo systemctl enable postgresql-16
sudo systemctl start postgresql-16

# Redis 7
sudo dnf install -y redis
sudo systemctl enable redis
sudo systemctl start redis

# Build tools
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y gcc git curl libpq-devel
```

### 4.2 — Configure PostgreSQL (RHEL/Rocky uses peer auth by default)

```bash
# Edit pg_hba.conf to allow password auth for local connections
sudo vi /var/lib/pgsql/16/data/pg_hba.conf

# Change this line:
# local   all   all   peer
# To:
# local   all   all   md5

# Restart PostgreSQL
sudo systemctl restart postgresql-16

# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE platform_dev;
CREATE USER platform_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE platform_dev TO platform_user;
ALTER DATABASE platform_dev OWNER TO platform_user;
\q
```

### 4.3 — Set up the project

```bash
git clone <your-repo-url> platform-backend
cd platform-backend

python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements/development.txt
```

---

## 5. Environment Configuration

```bash
# Copy the example file
cp .env.example .env

# Open and fill in your values
nano .env    # or: vim .env

# to generate the secret key from terminal
python -c "import secrets; print(secrets.token_hex(32))"

```

**Minimum required values for local dev:**

```env
DJANGO_ENV=development
DJANGO_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DJANGO_DEBUG=True

DB_NAME=platform_dev
DB_USER=platform_user
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379

JWT_SIGNING_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">

PLATFORM_NAME=MyPlatform
FRONTEND_URL=http://localhost:3000
SUPPORT_EMAIL=support@yourplatform.com
```

**Generate secure keys:**

```bash
# Secret key
python -c "import secrets; print(secrets.token_hex(32))"

# JWT signing key (use a different one from secret key)
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 6. First Run

Run these commands **once** after cloning or setting up a fresh environment:

```bash
# Activate virtual environment first
source venv/bin/activate

# Step 1: Apply all database migrations
python manage.py migrate

# Step 2: Seed default system config values
python manage.py seed_system_config

# Step 3: Collect static files
python manage.py collectstatic --noinput

# Step 4: Create ROOT user (CLI only — never via API)
python scripts/create_root_user.py
```

Expected output from migrate:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, roles, users, organizations, ...
Running migrations:
  Applying roles.0001_initial... OK
  Applying roles.0002_seed_roles... OK
  Applying users.0001_initial... OK
  ...
```

---

## 7. Running the Development Server

```bash
source venv/bin/activate

# Terminal 1 — Django API
python manage.py runserver 0.0.0.0:8000

# Terminal 2 — Celery Worker (for async tasks like emails)
celery -A config worker -l info

# Terminal 3 — Celery Beat (for scheduled tasks like cleanup)
celery -A config beat -l info
```

Or use the Makefile:

```bash
make run       # Django
make celery    # Celery worker
make beat      # Celery beat
```

**API is available at:** http://localhost:8000/api/v1/  
**Swagger docs:** http://localhost:8000/api/docs/  
**Admin panel:** http://localhost:8000/admin/

---

## 8. Staging Server Setup

Staging = a Linux server where you test before going live. Uses real PostgreSQL and Redis but without SSL (or with self-signed cert).

### 8.1 — Server requirements

- 2 vCPU, 2GB RAM minimum
- Ubuntu 22.04 LTS or Rocky Linux 9
- Docker + Docker Compose installed

### 8.2 — Install Docker (Ubuntu)

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (logout/login required after)
sudo usermod -aG docker $USER
```

### 8.3 — Install Docker (Rocky Linux 9)

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### 8.4 — Deploy to staging

```bash
# On the staging server
git clone <your-repo-url> /opt/platform
cd /opt/platform

# Create staging env file
cp .env.example .env.staging
nano .env.staging   # fill in staging values, DJANGO_ENV=staging

# Build the image
make docker-build

# Start staging stack
make docker-staging
```

### 8.5 — Run migrations on staging

```bash
docker compose -f docker/docker-compose.staging.yml exec api python manage.py migrate
docker compose -f docker/docker-compose.staging.yml exec api python manage.py seed_system_config
docker compose -f docker/docker-compose.staging.yml exec api python scripts/create_root_user.py
```

---

## 9. Production Server Setup (Ubuntu 22.04 LTS)

### 9.1 — Recommended server specs

| Load | CPU | RAM | Storage |
|---|---|---|---|
| < 1,000 users | 2 vCPU | 4 GB | 50 GB SSD |
| 1k–10k users | 4 vCPU | 8 GB | 100 GB SSD |
| 10k+ users | 8+ vCPU | 16+ GB | 200+ GB SSD + read replica |

### 9.2 — Initial server hardening

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create dedicated app user (never run as root)
sudo useradd -m -s /bin/bash platform
sudo usermod -aG sudo platform
sudo usermod -aG docker platform

# Set up SSH key authentication (do this from your local machine)
# ssh-copy-id platform@your-server-ip

# Disable password authentication (after setting up SSH keys)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Configure UFW firewall
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw deny 5432/tcp     # Block direct PostgreSQL access
sudo ufw deny 6379/tcp     # Block direct Redis access
sudo ufw enable
```

### 9.3 — Install Docker

```bash
# Same as staging (section 8.2 above)
sudo apt install -y ca-certificates curl gnupg
# ... (follow section 8.2 steps)
```

### 9.4 — Deploy application

```bash
# Switch to platform user
sudo su - platform

# Clone repository
git clone <your-repo-url> /opt/platform
cd /opt/platform

# Create production env file (secure permissions)
sudo mkdir -p /etc/platform
sudo touch /etc/platform/.env
sudo chown platform:platform /etc/platform/.env
sudo chmod 600 /etc/platform/.env

# Fill in production values
nano /etc/platform/.env
```

**Production .env values:**

```env
DJANGO_ENV=production
DJANGO_SECRET_KEY=<64-char random hex>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DEPLOYMENT_MODE=saas

DB_NAME=platform_prod
DB_USER=platform_user
DB_PASSWORD=<strong random password>
DB_HOST=db

REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
REDIS_PASSWORD=<strong random password>

JWT_SIGNING_KEY=<64-char random hex — different from SECRET_KEY>
JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7

# Email (SendGrid example)
EMAIL_BACKEND=anymail.backends.sendgrid.EmailBackend
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

PLATFORM_NAME=YourPlatform
FRONTEND_URL=https://yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com

CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Sentry (optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 9.5 — Build and start production stack

```bash
cd /opt/platform

# Build Docker image
make docker-build

# Start production stack
make docker-prod

# Run first-time setup
docker compose -f docker/docker-compose.prod.yml exec api python manage.py migrate
docker compose -f docker/docker-compose.prod.yml exec api python manage.py seed_system_config
docker compose -f docker/docker-compose.prod.yml exec api python manage.py collectstatic --noinput
docker compose -f docker/docker-compose.prod.yml exec api python scripts/create_root_user.py
```

---

## 10. Production Server Setup (Rocky Linux 9)

### 10.1 — Initial server setup

```bash
# Update system
sudo dnf update -y

# Install essential tools
sudo dnf install -y git curl wget vim firewalld

# Create app user
sudo useradd -m -s /bin/bash platform
sudo usermod -aG wheel platform

# Firewall configuration
sudo systemctl enable --now firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --remove-service=cockpit  # optional
sudo firewall-cmd --reload
```

### 10.2 — Install Docker on Rocky 9

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo systemctl enable --now docker
sudo usermod -aG docker platform

# SELinux adjustment for Docker volumes (Rocky Linux)
sudo setsebool -P container_manage_cgroup on
```

### 10.3 — Deploy (same as Ubuntu)

```bash
sudo su - platform
git clone <your-repo-url> /opt/platform
cd /opt/platform
# ... follow sections 9.4 and 9.5
```

---

## 11. SSL / HTTPS with Let's Encrypt

### 11.1 — Install Certbot (Ubuntu)

```bash
sudo apt install -y certbot
```

### 11.2 — Install Certbot (Rocky Linux)

```bash
sudo dnf install -y certbot
```

### 11.3 — Obtain SSL certificate

```bash
# Stop nginx temporarily if running
docker compose -f docker/docker-compose.prod.yml stop nginx

# Get certificate
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --non-interactive

# Certificates are saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Restart nginx
docker compose -f docker/docker-compose.prod.yml start nginx
```

### 11.4 — Auto-renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e
# Add this line:
0 2 * * * certbot renew --quiet && docker compose -f /opt/platform/docker/docker-compose.prod.yml exec nginx nginx -s reload
```

---

## 12. Systemd Service Management

Use this if you want the platform to start automatically on server boot.

### 12.1 — Install the service (Ubuntu and Rocky)

```bash
# Copy service file
sudo cp /opt/platform/docker/systemd/platform-api.service /etc/systemd/system/

# Update WorkingDirectory if your path differs
sudo nano /etc/systemd/system/platform-api.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable platform-api
sudo systemctl start platform-api

# Check status
sudo systemctl status platform-api
```

### 12.2 — Service management commands

```bash
sudo systemctl start platform-api      # Start
sudo systemctl stop platform-api       # Stop
sudo systemctl restart platform-api    # Restart
sudo systemctl reload platform-api     # Reload (pulls new image)
sudo systemctl status platform-api     # Status

# View logs
sudo journalctl -u platform-api -f     # Follow logs
sudo journalctl -u platform-api -n 100 # Last 100 lines
```

---

## 13. Redis Setup

### 13.1 — Desktop / local Redis

**Ubuntu/Debian:**
```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Test
redis-cli ping
# Expected: PONG
```

**Rocky/CentOS:**
```bash
sudo dnf install -y redis
sudo systemctl enable redis
sudo systemctl start redis

# Test
redis-cli ping
```

### 13.2 — Redis in Docker (development)

The `docker-compose.yml` in `docker/` already includes Redis. Just run:

```bash
make docker-dev
```

### 13.3 — Production Redis hardening

```bash
sudo nano /etc/redis/redis.conf    # Ubuntu
# OR
sudo nano /etc/redis.conf          # Rocky

# Make these changes:
requirepass YourStrongRedisPassword123!
bind 127.0.0.1
protected-mode yes
maxmemory 512mb
maxmemory-policy allkeys-lru
appendonly yes
```

```bash
# Restart Redis
sudo systemctl restart redis-server   # Ubuntu
sudo systemctl restart redis          # Rocky

# Test with password
redis-cli -a YourStrongRedisPassword123! ping
```

### 13.4 — Redis memory monitoring

```bash
# Check memory usage
redis-cli info memory | grep used_memory_human

# Check connected clients
redis-cli info clients

# Monitor real-time commands (useful for debugging)
redis-cli monitor
```

---

## 14. PostgreSQL Setup

### 14.1 — Desktop setup (Ubuntu)

```bash
# Install
sudo apt install -y postgresql-16 postgresql-client-16

# Start service
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE platform_dev;
CREATE USER platform_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE platform_dev TO platform_user;
ALTER DATABASE platform_dev OWNER TO platform_user;

-- For staging database:
CREATE DATABASE platform_staging;
GRANT ALL PRIVILEGES ON DATABASE platform_staging TO platform_user;
ALTER DATABASE platform_staging OWNER TO platform_user;

\q
```

### 14.2 — Desktop setup (Rocky/CentOS)

```bash
# Install PostgreSQL 16
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -qy module disable postgresql
sudo dnf install -y postgresql16-server postgresql16-contrib

# Initialize
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
sudo systemctl enable postgresql-16
sudo systemctl start postgresql-16

# Edit auth method (RHEL uses ident by default)
sudo nano /var/lib/pgsql/16/data/pg_hba.conf

# Find lines like:
# local   all   all   peer
# host    all   all   127.0.0.1/32   ident
# Change "peer" and "ident" to "md5":
# local   all   all   md5
# host    all   all   127.0.0.1/32   md5

sudo systemctl restart postgresql-16

# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE platform_dev;
CREATE USER platform_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE platform_dev TO platform_user;
ALTER DATABASE platform_dev OWNER TO platform_user;
\q
```

### 14.3 — Production PostgreSQL (inside Docker)

Production uses PostgreSQL inside Docker (handled by `docker-compose.prod.yml`). No manual setup needed — the container initialises automatically from the env vars.

### 14.4 — Useful PostgreSQL commands

```bash
# Connect to database
psql -U platform_user -d platform_dev -h localhost

# List all databases
psql -U postgres -c "\l"

# Check database size
psql -U platform_user -d platform_dev -c "SELECT pg_size_pretty(pg_database_size('platform_dev'));"

# Check active connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE datname='platform_dev';"

# Kill idle connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='platform_dev' AND state='idle' AND pid <> pg_backend_pid();"
```

---

## 15. Docker — Building & Deploying

### 15.1 — Build the production image

```bash
# From project root
docker build -f docker/Dockerfile -t platform-api:latest .

# Tag with version
docker build -f docker/Dockerfile -t platform-api:v1.0.0 .

# Save image to file (for delivery without registry)
docker save platform-api:v1.0.0 | gzip > platform-api-v1.0.0.tar.gz

# Load on another server
docker load < platform-api-v1.0.0.tar.gz
```

### 15.2 — Deploy update (zero-downtime)

```bash
cd /opt/platform

# Pull latest code
git pull origin main

# Rebuild image
make docker-build

# Rolling restart — Compose restarts containers one by one
make docker-prod

# Run any new migrations
docker compose -f docker/docker-compose.prod.yml exec api python manage.py migrate
```

### 15.3 — View container logs

```bash
# All services
docker compose -f docker/docker-compose.prod.yml logs -f

# API only
docker compose -f docker/docker-compose.prod.yml logs -f api

# Last 200 lines
docker compose -f docker/docker-compose.prod.yml logs --tail=200 api

# Celery worker
docker compose -f docker/docker-compose.prod.yml logs -f celery
```

### 15.4 — Execute commands inside container

```bash
# Open shell
docker compose -f docker/docker-compose.prod.yml exec api bash

# Run Django management commands
docker compose -f docker/docker-compose.prod.yml exec api python manage.py shell

# Check migration status
docker compose -f docker/docker-compose.prod.yml exec api python manage.py showmigrations
```

---

## 16. Makefile Quick Reference

```bash
make help               # Show all available commands

# Development
make install            # Install dev dependencies
make run                # Start Django dev server (port 8000)
make migrate            # Apply migrations
make migrations         # Create new migrations (make migrations app=users)
make seed               # Seed system config defaults
make shell              # Open Django shell
make celery             # Start Celery worker
make beat               # Start Celery Beat scheduler

# Testing
make test               # Run full test suite
make test-fast          # Run tests, stop on first failure
make test-app app=users # Test a specific app

# Code quality
make lint               # Run flake8
make format             # Auto-format with black + isort
make typecheck          # Run mypy

# Docker
make docker-dev         # Start dev stack (Postgres + Redis + Django)
make docker-build       # Build production image
make docker-prod        # Start production stack
make docker-prod-logs   # Tail production logs
make docker-staging     # Start staging stack

# Utilities
make clean              # Remove .pyc and __pycache__
make backup-db          # Backup production database
```

---

## 17. Creating the ROOT User

The ROOT user can **only** be created via CLI — never through the API. This is enforced by design.

```bash
# Local development
source venv/bin/activate
python scripts/create_root_user.py

# On staging/production (Docker)
docker compose -f docker/docker-compose.prod.yml exec api python scripts/create_root_user.py
```

You will be prompted for:
- Email address
- First name / Last name
- Password (min 10 chars, must be complex)

**After creating the ROOT user, immediately set up 2FA.** It is mandatory for ROOT.

---

## 18. Running Tests

```bash
source venv/bin/activate

# Run all tests with coverage
make test

# Run without coverage (faster)
make test-fast

# Run a specific app
make test-app app=authentication

# Run a specific test file
pytest apps/authentication/tests/test_services.py -v

# Run a specific test
pytest apps/authentication/tests/test_services.py::TestLogin::test_successful_login -v
```

---

## 19. Backup & Restore

### 19.1 — Database backup

```bash
# Backup (from container)
docker compose -f docker/docker-compose.prod.yml exec db \
  pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker compose -f docker/docker-compose.prod.yml exec db \
  pg_dump -U $DB_USER $DB_NAME | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Automated daily backup (add to crontab)
0 1 * * * cd /opt/platform && make backup-db
```

### 19.2 — Database restore

```bash
# Restore from backup
docker compose -f docker/docker-compose.prod.yml exec -T db \
  psql -U $DB_USER $DB_NAME < backup_20240101_010000.sql

# OR using make
make restore-db file=backup_20240101_010000.sql
```

### 19.3 — What to back up

| Data | Location | Frequency |
|---|---|---|
| PostgreSQL | Docker volume `postgres_data` | Daily |
| Uploaded media | Docker volume `media_files` | Daily |
| `.env` file | `/etc/platform/.env` | On every change |
| SSL certificates | `/etc/letsencrypt/` | Auto-renewed |

---

## 20. Security Hardening Checklist

Before going live, verify all of these:

```
Server
[ ] SSH key authentication only (password disabled)
[ ] Non-root user for all application processes
[ ] UFW/firewalld configured — only ports 22, 80, 443 open
[ ] PostgreSQL not accessible from outside (port 5432 blocked)
[ ] Redis not accessible from outside (port 6379 blocked)
[ ] fail2ban installed to block brute-force SSH attempts

Django
[ ] DJANGO_DEBUG=False in production
[ ] DJANGO_SECRET_KEY is 64+ random characters
[ ] JWT_SIGNING_KEY is 64+ random characters (different from SECRET_KEY)
[ ] ALLOWED_HOSTS set to your actual domain only
[ ] CORS_ALLOWED_ORIGINS set to your frontend domain only
[ ] SECURE_SSL_REDIRECT=True
[ ] SESSION_COOKIE_SECURE=True
[ ] CSRF_COOKIE_SECURE=True

Database
[ ] PostgreSQL uses a non-default strong password
[ ] pg_hba.conf restricts connections to localhost/Docker network only
[ ] Regular backups configured and tested

Redis
[ ] Redis requires password (requirepass set)
[ ] Redis bound to 127.0.0.1 only
[ ] Redis maxmemory configured

Application
[ ] ROOT user created and 2FA enabled
[ ] Default plan and license assigned to first org
[ ] System config seeded (python manage.py seed_system_config)
[ ] Email provider configured and tested (send a test invite)
[ ] Sentry DSN configured for error tracking
[ ] Health check endpoint responding: curl https://yourdomain.com/api/health/
```

---

## 21. Troubleshooting

### Database connection refused

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql    # Ubuntu
sudo systemctl status postgresql-16 # Rocky

# Check it's listening
sudo -u postgres psql -c "SELECT 1;"

# Check .env DB_HOST (should be 'localhost' for local, 'db' for Docker)
grep DB_HOST .env
```

### Redis connection refused

```bash
# Check Redis is running
sudo systemctl status redis-server  # Ubuntu
sudo systemctl status redis         # Rocky

# Test connection
redis-cli ping                 # No password
redis-cli -a yourpassword ping # With password

# Check which port Redis is on
sudo ss -tlnp | grep 6379
```

### Migrations fail

```bash
# Check migration status
python manage.py showmigrations

# If a migration is broken, check for circular dependencies
python manage.py migrate --check

# Reset migrations (DEVELOPMENT ONLY — destroys all data)
# python manage.py migrate <app> zero
```

### Celery tasks not running

```bash
# Check Celery worker is running
celery -A config inspect active

# Check Redis broker connection
celery -A config inspect ping

# Check registered tasks
celery -A config inspect registered
```

### 500 errors in production

```bash
# Check Django logs
docker compose -f docker/docker-compose.prod.yml logs api | grep ERROR

# Enable temporary debug (never leave this on)
# DJANGO_DEBUG=True in .env, then restart

# Check health endpoint
curl http://localhost:8000/api/health/
```

### Permission denied on Docker volumes

```bash
# Fix ownership of Docker volumes
sudo chown -R 1000:1000 /opt/platform
```

---

## Quick Start Summary

```bash
# 1. Install PostgreSQL and Redis (section 3 or 4)
# 2. Create database (section 14.1 or 14.2)
# 3. Clone repo and install dependencies
git clone <repo> && cd platform-backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt

# 4. Configure environment
cp .env.example .env && nano .env

# 5. First run
python manage.py migrate
python manage.py seed_system_config
python scripts/create_root_user.py

# 6. Start
make run        # Terminal 1
make celery     # Terminal 2
```

API: http://localhost:8000/api/v1/  
Docs: http://localhost:8000/api/docs/  
Admin: http://localhost:8000/admin/

---

*Built with Django 4.2 · PostgreSQL 16 · Redis 7 · Celery 5*
