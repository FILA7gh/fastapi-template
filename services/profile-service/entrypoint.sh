#!/bin/sh
export PYTHONPATH=/opt/services/profile-service:$PYTHONPATH

export PGPASSWORD="$POSTGRES_PASSWORD"

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Waiting for postgres..."
  sleep 2
done

psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE SCHEMA IF NOT EXISTS profile;"

echo "Start migrations"
alembic upgrade head

cd /opt/services/profile-service/src

echo "Start server"
uvicorn main:get_app --factory --host 0.0.0.0 --port 8000 --reload --log-level info