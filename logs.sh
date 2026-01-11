#!/bin/bash

# MeterSphere Python Backend - 查看日誌腳本
# 從項目根目錄運行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend_python"

# 進入後端目錄
cd "${BACKEND_DIR}"

# 獲取服務名稱（如果提供）
SERVICE=${1:-""}

echo "📋 MeterSphere Python Backend - 查看日誌"
echo "========================================"

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    exit 1
fi

# 查看日誌
if [ -z "$SERVICE" ]; then
    echo "查看所有服務日誌（按 Ctrl+C 退出）..."
    if docker compose version &> /dev/null; then
        docker compose logs -f
    else
        docker-compose logs -f
    fi
else
    echo "查看 $SERVICE 服務日誌（按 Ctrl+C 退出）..."
    if docker compose version &> /dev/null; then
        docker compose logs -f "$SERVICE"
    else
        docker-compose logs -f "$SERVICE"
    fi
fi

