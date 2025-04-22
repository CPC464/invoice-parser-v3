#!/bin/bash

# Script to reset the invoice parser application, including database

echo "Stopping all services..."
docker-compose down

echo "Removing database..."
rm -f backend/db/db.sqlite3

echo "Removing media files..."
rm -rf backend/media/uploads/*

echo "Rebuilding and starting services..."
docker-compose up -d --build

echo "Waiting for services to initialize..."
sleep 10

echo "Creating admin user..."
docker-compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"

echo "System reset complete!"
echo "Backend API: http://localhost:8888"
echo "API Docs:    http://localhost:8888/api/docs/"
echo "Frontend UI: http://localhost:8501"
echo "Admin panel: http://localhost:8888/admin/"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: adminpassword" 