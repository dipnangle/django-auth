#!/bin/bash
set -e

echo "=== Platform Backend Starting ==="

# Wait for DB
echo "Waiting for database..."
until python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('DB ready')
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files (production only)
if [ "$DJANGO_ENV" = "production" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
fi

# Seed system config defaults
echo "Seeding system config..."
python manage.py seed_system_config || true

echo "=== Starting server ==="
exec "$@"
