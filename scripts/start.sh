#!/bin/bash

# Script to start the invoice parser application

# Read superuser credentials from backend/.env.local for display at the end
if [ -f ./backend/.env.local ]; then
    source ./backend/.env.local
else
    echo "Warning: backend/.env.local not found"
fi

echo "Starting Invoice Parser services..."
docker-compose up -d

echo "Waiting for services to initialize..."
sleep 5

echo "Checking superuser..."
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
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

echo "Services started successfully!"
echo "Backend API: http://localhost:8888"
echo "API Docs:    http://localhost:8888/api/docs/"
echo "Frontend UI: http://localhost:8501"
echo "Admin panel: http://localhost:8888/admin/"
echo ""
echo "Admin credentials:"
echo "Username: ${DJANGO_SUPERUSER_USERNAME}"
echo "Password: ${DJANGO_SUPERUSER_PASSWORD}" 