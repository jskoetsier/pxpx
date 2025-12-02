#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -U pxmx_user; do
  sleep 1
done

echo "PostgreSQL is ready!"

# Give Redis a moment to start
echo "Waiting for Redis..."
sleep 5

echo "Redis should be ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: username=admin, password=admin')
else:
    print('Superuser already exists')
END

echo "Starting application..."
exec "$@"
