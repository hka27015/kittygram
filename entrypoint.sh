#!/bin/sh

set -e

echo "migrations..."
python manage.py migrate --noinput

echo "collect static..."
python manage.py collectstatic --noinput

echo "run server..."
exec gunicorn kittygram.wsgi:application --bind 0.0.0.0:8000