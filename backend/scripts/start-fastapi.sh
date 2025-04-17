#!/bin/bash
# Startup script for FastAPI backend

set -e

echo "Starting FastAPI backend..."

# Wait for database services
echo "Waiting for PostgreSQL..."
while ! nc -z ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432}; do
  sleep 1
done

echo "Waiting for MongoDB..."
while ! nc -z ${MONGODB_HOST:-mongodb} ${MONGODB_PORT:-27017}; do
  sleep 1
done

echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 1
done

echo "All database services are ready!"

# Start the FastAPI application with uvicorn
echo "Starting FastAPI server with uvicorn..."
exec uvicorn fastapi_app.main:app \
    --host 0.0.0.0 \
    --port ${FASTAPI_PORT:-8000} \
    --workers ${WORKERS:-4} \
    --log-level ${LOG_LEVEL:-info}