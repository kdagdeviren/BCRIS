# BCRIS - Production Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="dagdeviren.kagan@gmail.com"
LABEL description="BCRIS - Breast Cancer Response Intelligence System"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn psycopg2-binary whitenoise

# Copy project files
COPY . .

# Create necessary directories for volumes
RUN mkdir -p /app/media/ml_models \
    /app/media/patient_data \
    /app/media/downloadable_files \
    /app/staticfiles \
    /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create a non-root user
RUN useradd -m -u 1000 bcris && \
    chown -R bcris:bcris /app

# Switch to non-root user
USER bcris

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "/app/logs/access.log", "--error-logfile", "/app/logs/error.log", "bcris_project.wsgi:application"]
