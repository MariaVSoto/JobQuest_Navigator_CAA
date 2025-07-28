# Multi-stage Dockerfile for FastAPI + Strawberry GraphQL Backend
# Optimized for AWS ECS production deployment with security and performance focus

# ============================================================================
# Stage 1: Base Python image with optimized dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set production-optimized environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    DEBIAN_FRONTEND=noninteractive

# Update system and install essential dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential build tools
    build-essential \
    gcc \
    g++ \
    # PostgreSQL client libraries
    libpq-dev \
    # Network tools for health checks
    curl \
    wget \
    # SSL/TLS support
    ca-certificates \
    # Process monitoring
    procps \
    # Timezone data
    tzdata \
    # Magic library for file type detection
    libmagic-dev \
    # Clean up in same layer to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create app directory and non-root user early
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app --shell=/bin/bash appuser

WORKDIR /app

# ============================================================================
# Stage 2: Dependencies installation stage
# ============================================================================
FROM base as dependencies

# Copy and install Python dependencies
COPY requirements.txt requirements-prod.txt* ./

# Install production dependencies with optimizations
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 3: Development image with hot reload
# ============================================================================
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    watchdog \
    pytest \
    pytest-asyncio \
    pytest-cov \
    httpx \
    black \
    isort \
    flake8 \
    mypy

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command for development (with auto-reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

# ============================================================================
# Stage 4: Production image (security and performance optimized)
# ============================================================================
FROM dependencies as production

# Production environment variables
ENV ENVIRONMENT=production \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000 \
    UVICORN_WORKERS=4 \
    UVICORN_LOG_LEVEL=info \
    UVICORN_ACCESS_LOG=true \
    UVICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker \
    UVICORN_WORKER_CONNECTIONS=1000 \
    UVICORN_MAX_REQUESTS=1000 \
    UVICORN_MAX_REQUESTS_JITTER=50

# Copy only necessary application files (exclude dev files)
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser run_dev.py ./

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    # Create specific permission for logs
    chmod 777 /app/logs

# Remove unnecessary packages to reduce attack surface
RUN apt-get update && apt-get remove -y \
    build-essential \
    gcc \
    g++ \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER appuser

# Production health check with better timing
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production startup script for graceful shutdown and monitoring
CMD ["sh", "-c", "uvicorn app.main:app --host $UVICORN_HOST --port $UVICORN_PORT --workers $UVICORN_WORKERS --log-level $UVICORN_LOG_LEVEL --access-log $UVICORN_ACCESS_LOG --worker-class $UVICORN_WORKER_CLASS --worker-connections $UVICORN_WORKER_CONNECTIONS --max-requests $UVICORN_MAX_REQUESTS --max-requests-jitter $UVICORN_MAX_REQUESTS_JITTER"]

# ============================================================================
# Stage 5: AWS ECS optimized production image
# ============================================================================
FROM production as ecs-production

# ECS-specific environment variables
ENV AWS_DEFAULT_REGION=us-east-1 \
    AWS_REGION=us-east-1 \
    ECS_ENABLE_LOGGING=true \
    ECS_ENABLE_CONTAINER_METADATA=true

# Install AWS CLI tools for ECS integration (minimal)
USER root
RUN pip install --no-cache-dir awscli-local boto3 && \
    pip cache purge

# Switch back to non-root user
USER appuser

# ECS-optimized health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Signal handling for graceful shutdown in ECS
STOPSIGNAL SIGTERM

# ECS production command with proper signal handling
CMD ["sh", "-c", "exec uvicorn app.main:app --host $UVICORN_HOST --port $UVICORN_PORT --workers $UVICORN_WORKERS --log-level $UVICORN_LOG_LEVEL --access-log --worker-class uvicorn.workers.UvicornWorker --worker-connections $UVICORN_WORKER_CONNECTIONS --max-requests $UVICORN_MAX_REQUESTS --max-requests-jitter $UVICORN_MAX_REQUESTS_JITTER"]

# Default target is development
FROM development