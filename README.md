# Invoice Parser System

A complete system for uploading, managing, and processing invoice files. Built with Django REST Framework backend and Streamlit frontend, running in Docker containers.

## Features

- File upload and management with Django REST Framework
- User-friendly file management interface with Streamlit
- API documentation with Swagger/Redoc
- Docker containerization for easy deployment
- Single command to start and reset the application

## System Architecture

- **Backend:** Django + Django REST Framework + SQLite
- **Frontend:** Streamlit
- **Database:** SQLite (persistent via Docker volumes)
- **Container Orchestration:** Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Properly configured .env.local files in backend/ and frontend/ directories

### Starting the Application

```bash
./scripts/start.sh
```

This will:

1. Build and start the Docker containers
2. Set up the database
3. Start the backend Django server on port 8888
4. Start the frontend Streamlit app on port 8501
5. Create a Django superuser using credentials from backend/.env.local (if one doesn't exist)

### Resetting the Application

If you need to reset the database and start fresh:

```bash
./scripts/reset.sh
```

This will:

1. Stop all containers
2. Remove the database file
3. Clean up media files
4. Rebuild and restart the application
5. Create a new admin user using credentials from backend/.env.local (if one doesn't exist)

## Accessing the Applications

- **Frontend UI:** http://localhost:8501
- **Backend API:** http://localhost:8888/api/v1/
- **API Documentation:** http://localhost:8888/api/docs/
- **Admin Panel:** http://localhost:8888/admin/

### Admin Credentials

The system uses the admin credentials specified in your backend/.env.local file:

```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

These credentials must be properly set in the .env.local file for the superuser creation to work.

## API Endpoints

The system provides the following REST API endpoints:

- `GET /api/v1/files/`: List all files
- `POST /api/v1/files/`: Upload a new file
- `GET /api/v1/files/{id}/`: Get file details
- `PATCH /api/v1/files/{id}/`: Update file metadata
- `DELETE /api/v1/files/{id}/`: Delete a file
- `GET /health/`: Health check endpoint

## Project Structure

```
.
├── backend/                # Django backend
│   ├── config/             # Django project settings
│   ├── files/              # Files app
│   ├── db/                 # SQLite database location
│   └── media/              # Media storage
├── frontend/               # Streamlit frontend
├── scripts/                # Utility scripts
│   ├── start.sh            # Start the application
│   └── reset.sh            # Reset the application
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile.backend      # Backend container definition
└── Dockerfile.frontend     # Frontend container definition
```

## Development

### Environment Variables

The application uses environment variables for configuration. Sample environment files are provided:

- `backend/.env.example`: Backend environment variables
- `frontend/.env.example`: Frontend environment variables

Create your own `.env.local` files based on these examples to customize your environment.

### Adding Features

1. **Backend**: Add new models, serializers, and views in the Django application
2. **Frontend**: Extend the Streamlit application with additional pages and functionality
3. **Build**: Run `docker-compose build` to rebuild after changes

## Troubleshooting

- If the frontend can't connect to the backend, check that the services are running with `docker-compose ps`
- For database issues, try resetting the application with `./scripts/reset.sh`
- Check Docker logs with `docker-compose logs`

## Future Enhancements

- Add user authentication on the frontend
- Implement invoice data extraction functionality
- Add support for more file types
- Create a reporting interface for parsed invoices
