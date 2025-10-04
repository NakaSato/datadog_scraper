#!/bin/bash

# Docker Deployment Script for Datadog Scraper
# This script helps you manage Docker containers for the scraper service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  up          Start the scraper service"
    echo "  down        Stop the scraper service"
    echo "  logs        Show service logs"
    echo "  status      Show service status"
    echo "  restart     Restart the scraper service"
    echo "  clean       Remove containers and images"
    echo "  n8n         Start with n8n (requires docker-compose.n8n.yml)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 up    # Build and start the service"
    echo "  $0 logs -f           # Follow logs"
    echo "  $0 n8n               # Start with n8n integration"
}

# Check if docker-compose exists
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}Error: docker-compose or 'docker compose' is not installed.${NC}"
        exit 1
    fi
}

# Build the Docker image
build() {
    echo -e "${BLUE}Building Docker image...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose build
    else
        docker compose build
    fi
    echo -e "${GREEN}Docker image built successfully!${NC}"
}

# Start the service
up() {
    echo -e "${BLUE}Starting Datadog Scraper service...${NC}"

    # Load environment variables if .env exists
    if [[ -f .env ]]; then
        echo -e "${YELLOW}Loading environment from .env file...${NC}"
        source .env
    fi

    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi

    echo -e "${GREEN}Service started!${NC}"
    echo -e "${BLUE}API Documentation: http://localhost:${PORT:-8000}/docs${NC}"
    echo -e "${BLUE}Health Check: http://localhost:${PORT:-8000}/health${NC}"
}

# Start with n8n
n8n() {
    echo -e "${BLUE}Starting Datadog Scraper with n8n...${NC}"

    if [[ ! -f docker-compose.n8n.yml ]]; then
        echo -e "${YELLOW}Creating n8n docker-compose file...${NC}"
        cat > docker-compose.n8n.yml << 'EOF'
version: '3.8'

services:
  datadog-scraper:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: datadog-scraper
    environment:
      - MAX_DEPTH=${MAX_DEPTH:-2}
      - DELAY=${DELAY:-0.5}
      - HOST=${HOST:-0.0.0.0}
      - PORT=${PORT:-8000}
    ports:
      - "${PORT:-8000}:8000"
    volumes:
      - ./output:/app/output:rw
    networks:
      - scraper-network
    restart: unless-stopped

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-local
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-password}
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=${N8N_PORT:-5678}
      - GENERIC_TIMEZONE=${TZ:-UTC}
    ports:
      - "${N8N_PORT:-5678}:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - scraper-network
    restart: unless-stopped
    depends_on:
      - datadog-scraper

volumes:
  n8n_data:
    driver: local

networks:
  scraper-network:
    driver: bridge
EOF
    fi

    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.n8n.yml up -d
    else
        docker compose -f docker-compose.n8n.yml up -d
    fi

    echo -e "${GREEN}Services started!${NC}"
    echo -e "${BLUE}Scraper API: http://localhost:${PORT:-8000}/docs${NC}"
    echo -e "${BLUE}n8n: http://localhost:${N8N_PORT:-5678}${NC}"
}

# Stop the service
down() {
    echo -e "${BLUE}Stopping services...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    echo -e "${GREEN}Services stopped.${NC}"
}

# Show logs
logs() {
    if command -v docker-compose &> /dev/null; then
        docker-compose logs "$@"
    else
        docker compose logs "$@"
    fi
}

# Show status
status() {
    echo -e "${BLUE}Service Status:${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

# Restart service
restart() {
    echo -e "${BLUE}Restarting service...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose restart
    else
        docker compose restart
    fi
    echo -e "${GREEN}Service restarted.${NC}"
}

# Clean up
clean() {
    echo -e "${YELLOW}This will remove containers, networks, and images. Are you sure? (y/N)${NC}"
    read -r confirm
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        echo -e "${BLUE}Cleaning up...${NC}"
        if command -v docker-compose &> /dev/null; then
            docker-compose down --volumes --rmi all
        else
            docker compose down --volumes --rmi all
        fi
        echo -e "${GREEN}Cleanup completed.${NC}"
    else
        echo -e "${YELLOW}Cleanup cancelled.${NC}"
    fi
}

# Main logic
check_docker_compose

case "${1:-help}" in
    build)
        build
        ;;
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs "${@:2}"
        ;;
    status)
        status
        ;;
    restart)
        restart
        ;;
    clean)
        clean
        ;;
    n8n)
        n8n
        ;;
    help|*)
        usage
        ;;
esac
