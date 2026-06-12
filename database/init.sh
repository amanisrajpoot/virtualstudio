#!/bin/bash
set -e

echo "Running migrations..."
for f in /docker-entrypoint-initdb.d/migrations/*.sql; do
    echo "Applying $f"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$f"
done

echo "Running seeds..."
for f in /docker-entrypoint-initdb.d/seeds/*.sql; do
    echo "Applying $f"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$f"
done
