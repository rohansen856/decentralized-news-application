#!/bin/bash
# Startup script for Flask backend

set -e

echo "Starting Flask backend..."

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

# Run database migrations if needed
# python -m flask_app.migrations

# Start the Flask application
echo "Starting Flask server..."
exec python -m flask_app.app