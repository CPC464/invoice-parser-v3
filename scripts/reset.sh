#!/bin/bash

# Script to reset the invoice parser application, including database

# Read superuser credentials from backend/.env.local for display at the end
if [ -f ./backend/.env.local ]; then
    source ./backend/.env.local
else
    echo "Warning: backend/.env.local not found"
fi

echo "Stopping all services..."
docker-compose down

echo "Removing Docker volumes for database and media..."
docker volume rm invoice-parser-v3_db_data invoice-parser-v3_media_data || true

echo "Rebuilding and starting services with fresh volumes..."
docker-compose up -d --build

echo "Waiting for services to initialize..."
sleep 10

# Run migrations first to create database tables
echo "Running database migrations..."
docker-compose exec backend python manage.py migrate

# Now create the superuser after tables exist
echo "Creating superuser from environment variables..."
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
from django.conf import settings
import os

# Get values from environment - these should be loaded from .env.local
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# Ensure all required variables are set
if not username or not email or not password:
    print('ERROR: One or more required environment variables are not set.')
    print('Make sure DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD')
    print('are properly defined in backend/.env.local and passed to the container.')
    import sys
    sys.exit(1)

# Check if the superuser already exists
if User.objects.filter(username=username).exists():
    print(f'Superuser {username} already exists')
else:
    User.objects.create_superuser(username, email, password)
    print(f'Created superuser {username}')
"

echo "System reset complete!"
echo "Backend API: http://localhost:8888"
echo "API Docs:    http://localhost:8888/api/docs/"
echo "Frontend UI: http://localhost:8501"
echo "Admin panel: http://localhost:8888/admin/"
echo ""
echo "Admin credentials:"
echo "Username: ${DJANGO_SUPERUSER_USERNAME}"
echo "Password: ${DJANGO_SUPERUSER_PASSWORD}" 