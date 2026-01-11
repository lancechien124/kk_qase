#!/bin/bash

# MeterSphere Python Backend Restore Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR=${BACKUP_DIR:-./backups}
BACKUP_FILE=${1:-""}
MYSQL_CONTAINER=${MYSQL_CONTAINER:-metersphere-mysql}
MYSQL_USER=${MYSQL_USER:-root}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-metersphere}

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Please specify backup file${NC}"
    echo "Usage: $0 <backup_file_prefix>"
    echo "Example: $0 database_20240101_120000"
    exit 1
fi

echo -e "${YELLOW}Warning: This will restore from backup. Continue? (y/N)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Restore database
if [ -f "$BACKUP_DIR/${BACKUP_FILE}.sql.gz" ]; then
    echo -e "${GREEN}Restoring database...${NC}"
    gunzip -c $BACKUP_DIR/${BACKUP_FILE}.sql.gz | \
        docker exec -i $MYSQL_CONTAINER mysql \
            -u $MYSQL_USER \
            -p$MYSQL_PASSWORD \
            $MYSQL_DATABASE
    echo -e "${GREEN}Database restored successfully!${NC}"
else
    echo -e "${YELLOW}Database backup file not found: $BACKUP_DIR/${BACKUP_FILE}.sql.gz${NC}"
fi

# Restore Redis data
if [ -f "$BACKUP_DIR/redis_${BACKUP_FILE#database_}.rdb" ]; then
    echo -e "${GREEN}Restoring Redis data...${NC}"
    docker cp $BACKUP_DIR/redis_${BACKUP_FILE#database_}.rdb metersphere-redis:/data/dump.rdb
    docker restart metersphere-redis
    echo -e "${GREEN}Redis data restored successfully!${NC}"
fi

# Restore uploads
if [ -f "$BACKUP_DIR/uploads_${BACKUP_FILE#database_}.tar.gz" ]; then
    echo -e "${GREEN}Restoring uploads...${NC}"
    tar -xzf $BACKUP_DIR/uploads_${BACKUP_FILE#database_}.tar.gz
    echo -e "${GREEN}Uploads restored successfully!${NC}"
fi

echo -e "${GREEN}Restore completed successfully!${NC}"

