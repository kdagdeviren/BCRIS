#!/bin/bash
# BCRIS Start Script

set -e

echo "🚀 Starting BCRIS..."

# Wait for database
echo "⏳ Waiting for database..."
python << END
import sys
import time
import psycopg2
import os

max_retries = 30
retry_interval = 2

for i in range(max_retries):
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('POSTGRES_DB', 'bcris'),
            user=os.environ.get('POSTGRES_USER', 'bcris_user'),
            password=os.environ.get('POSTGRES_PASSWORD', ''),
            host=os.environ.get('POSTGRES_HOST', 'db'),
            port=os.environ.get('POSTGRES_PORT', '5432')
        )
        conn.close()
        print("✅ Database is ready!")
        sys.exit(0)
    except psycopg2.OperationalError:
        if i < max_retries - 1:
            print(f"⏳ Database not ready, retrying... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
        else:
            print("❌ Database connection failed!")
            sys.exit(1)
END

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if not exists (optional)
# python manage.py shell << END
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'admin')
#     print("✅ Superuser created!")
# END

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
