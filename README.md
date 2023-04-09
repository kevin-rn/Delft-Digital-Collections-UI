# IR-Project

This repository contains all code related to the Information Retrieval Project.

# Run webservice
The service is containerized via Docker.
You can either run the service in development mode via:
`$ docker compose up -d --build` and navigating to http://localhost:5000

or in production mode via
`$ docker compose -f "docker-compose.prod.yml" up -d --build` and navigating to http://localhost:80

# Differences Development vs Production
The service is powered by Gunicorn instead of the built-in flask server.
The service is behind a reverse proxy
The container is hardened; running as non-root user and has no access to the local file system
Extensive logging aimed for development and debugging is turned off