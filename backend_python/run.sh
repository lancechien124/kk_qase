#!/bin/bash

# MeterSphere Python Backend Run Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting MeterSphere Python Backend...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r ../requirements.txt
    touch venv/.installed
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Please create one.${NC}"
fi

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
alembic upgrade head

# Run application
echo -e "${GREEN}Starting application...${NC}"
if [ "$ENVIRONMENT" = "production" ]; then
    gunicorn main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8081 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
else
    python main.py
fi
