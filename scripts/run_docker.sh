#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/utils.sh"

COMPOSE_FILE="docker-compose.yml"

# Check if the compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    log "Compose file ($COMPOSE_FILE) not found. Exiting..."
    exit 1
fi

# Pull down any existing container and remove unused images
log "Stopping and removing any existing services..."
docker compose down --remove-orphans || error "Failed to stop running services."

# Build and start services
log "Building $COMPOSE_FILE..."
docker compose up --build -d || { error "Failed to start services."; exit 1; }

log "Services are running. Use 'docker compose logs -f' to view logs."