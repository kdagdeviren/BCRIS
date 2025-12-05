#!/bin/bash
# BCRIS Start Script

set -e

echo "🚀 Starting BCRIS with SQLite..."

# Ensure volume directories exist
echo "📁 Setting up volume directories..."
mkdir -p /app/data /app/media /app/staticfiles /app/logs /app/models

# Fix permissions for volume directories (in case they're mounted as root)
echo "� Fixingg permissions..."
chmod -R 777 /app/data /app/media /app/staticfiles /app/logs /app/models 2>/dev/null || true

# Run migrations
echo "� Rulnning migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ BCRIS is ready!"

# Start Gunicorn
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info \
    bcris_project.wsgi:application
