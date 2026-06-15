#!/bin/sh

echo "Waiting for database..."

while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 0.5
done

echo "Database is ready!"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"