#!/bin/bash

# MeterSphere Python Backend Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo -e "${GREEN}Starting MeterSphere Python Backend deployment...${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your configuration.${NC}"
    else
        echo -e "${RED}Error: .env.example file not found.${NC}"
        exit 1
    fi
fi

# Build and start services
echo -e "${GREEN}Building and starting services...${NC}"
if docker compose version &> /dev/null; then
    docker compose -f $COMPOSE_FILE up -d --build
else
    docker-compose -f $COMPOSE_FILE up -d --build
fi

# Wait for services to be ready
echo -e "${GREEN}Waiting for services to be ready...${NC}"
sleep 10

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
if docker compose version &> /dev/null; then
    docker compose -f $COMPOSE_FILE exec -T backend python -m alembic upgrade head
else
    docker-compose -f $COMPOSE_FILE exec -T backend python -m alembic upgrade head
fi

# Check health
echo -e "${GREEN}Checking service health...${NC}"
sleep 5

if curl -f http://localhost:8081/api/v1/health/live &> /dev/null; then
    echo -e "${GREEN}✓ Service is healthy!${NC}"
    echo -e "${GREEN}API is available at: http://localhost:8081${NC}"
    echo -e "${GREEN}Swagger UI is available at: http://localhost:8081/api/docs${NC}"
else
    echo -e "${RED}✗ Service health check failed. Please check logs.${NC}"
    if docker compose version &> /dev/null; then
        docker compose -f $COMPOSE_FILE logs backend
    else
        docker-compose -f $COMPOSE_FILE logs backend
    fi
    exit 1
fi

echo -e "${GREEN}Deployment completed successfully!${NC}"

