#!/bin/bash

# Script to start the invoice parser application

echo "Starting Invoice Parser services..."
docker-compose up -d

echo "Waiting for services to initialize..."
sleep 5

echo "Services started successfully!"
echo "Backend API: http://localhost:8888"
echo "API Docs:    http://localhost:8888/api/docs/"
echo "Frontend UI: http://localhost:8501"
echo "Admin panel: http://localhost:8888/admin/"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: adminpassword" 