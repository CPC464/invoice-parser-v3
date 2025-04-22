Create a complete Django project with Django Rest Framework (DRF) backend and Streamlit frontend. The project should use SQLite for the database and run in Docker containers. The entire setup should be able to start with a single command, and there should be a way to reset the database and restart the project with a single command.

# Technical Requirements:

1. Docker and Docker Compose setup for containerization
2. Django + DRF backend
3. Streamlit frontend
4. SQLite database
5. Communication between frontend and backend containers
6. Database reset functionality
7. Single command project startup

# Project Structure:

The project should have the following structure:

- backend/ (Django + DRF)
  - .env.example
  - .env.local (actual environment variables, to be gitignored)
  - config/
    - settings.py
    - urls.py (Overall routing, but urls should be defined within each app and just 'consolidated' here)
- frontend/ (Streamlit)
  - .env.example
  - .env.local (actual environment variables, to be gitignored)
- docker-compose.yml
- Dockerfile.backend
- Dockerfile.frontend
- scripts/ (containing start and reset scripts)

NB: This structure does not list all files, so add additional files as needed

# Specific Implementation Details:

## Backend (Django + DRF):

- Create a Django project with at least one sample app
- Set up Django Rest Framework with DRF ViewSets (not functional views) and DRF SimpleRouter
- Configure Django to use SQLite database located in a volume for persistence
- Create a files app with full crud operations so a user can upload files. Keep the implementation to an MVP. We will build on this later. Save the original_file_name and make it possible for the user to save a user_defined_file_name (optional)
- Use UUIDs for all models as primary keys
- Configure the admin for the demo model
- Implement API documentation using drf-spectacular
- Include health check endpoints

## Frontend (Streamlit):

- Create a Streamlit application that communicates with the Django backend API
- Implement a UI for CRUD operations for the files endpoint. It should be possible to upload a file, see a list of files and and delete files from the list. It should also be possible to specify an optional file name and to change the file name
- Include proper error handling and loading states
- Make the UI responsive and user-friendly

## Docker Configuration:

- Create Dockerfiles for both backend and frontend
- Set up a Docker Compose file that orchestrates all services
- Configure proper networking between services
- Mount volumes for the SQLite database and code for development

## Scripts:

- Create a start script that uses 'docker-compose up'
- Create a reset script that stops containers, removes the database file, and restarts everything
- Make scripts executable and available in the PATH

## Documentation:

- Include comprehensive README.md with setup and usage instructions
- Document API endpoints using drf-spectacular
- Provide examples of using the application

Please provide all the necessary code, configuration files, and scripts to implement this project. Also, explain how to use the system, including how to start the project and how to reset the database.
