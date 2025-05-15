#!/bin/sh

set -e

# Wait for Redis
until nc -z redis 6379; do
  echo "Waiting for Redis..."
  sleep 1
done

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create celerybeat schedule file if needed
if [ "$CELERY_BEAT" = "true" ]; then
  python manage.py celerybeat_init
fi

exec "$@"