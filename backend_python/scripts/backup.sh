#!/bin/bash

# MeterSphere Python Backend Backup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR=${BACKUP_DIR:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MYSQL_CONTAINER=${MYSQL_CONTAINER:-metersphere-mysql}
MYSQL_USER=${MYSQL_USER:-root}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-metersphere}

echo -e "${GREEN}Starting backup...${NC}"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo -e "${GREEN}Backing up database...${NC}"
docker exec $MYSQL_CONTAINER mysqldump \
    -u $MYSQL_USER \
    -p$MYSQL_PASSWORD \
    $MYSQL_DATABASE > $BACKUP_DIR/database_$TIMESTAMP.sql

# Compress database backup
gzip $BACKUP_DIR/database_$TIMESTAMP.sql

# Backup Redis data (if using persistence)
if docker ps | grep -q metersphere-redis; then
    echo -e "${GREEN}Backing up Redis data...${NC}"
    docker exec metersphere-redis redis-cli --rdb /data/dump.rdb
    docker cp metersphere-redis:/data/dump.rdb $BACKUP_DIR/redis_$TIMESTAMP.rdb
fi

# Backup uploads directory
if [ -d "./uploads" ]; then
    echo -e "${GREEN}Backing up uploads...${NC}"
    tar -czf $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz ./uploads
fi

# Backup logs (optional)
if [ -d "./logs" ]; then
    echo -e "${GREEN}Backing up logs...${NC}"
    tar -czf $BACKUP_DIR/logs_$TIMESTAMP.tar.gz ./logs
fi

echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "${GREEN}Backup location: $BACKUP_DIR${NC}"

# List backup files
ls -lh $BACKUP_DIR/*$TIMESTAMP*

