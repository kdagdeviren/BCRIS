#!/bin/bash
# BCRIS Start Script

set -e

echo "🚀 Starting BCRIS..."

# Wait for database (if using PostgreSQL)
if [ -n "$POSTGRES_HOST" ]; then
    echo "⏳ Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
    
    max_retries=30
    counter=0
    
    until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
        counter=$((counter+1))
        if [ $counter -gt $max_retries ]; then
            echo "❌ PostgreSQL did not become ready in time"
            exit 1
        fi
        echo "⏳ Waiting for PostgreSQL... ($counter/$max_retries)"
        sleep 2
    done
    
    echo "✅ PostgreSQL is ready!"
else
    echo "ℹ️ Using SQLite database"
fi

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

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
