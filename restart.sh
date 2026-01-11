#!/bin/bash

# MeterSphere Python Backend - 重啟腳本
# 從項目根目錄運行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend_python"

echo "🔄 MeterSphere Python Backend - 重啟服務"
echo "========================================"

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 進入後端目錄
cd "${BACKEND_DIR}"

# 重啟服務
echo "🔄 重啟 Docker 服務..."
if docker compose version &> /dev/null; then
    docker compose restart
else
    docker-compose restart
fi

# 等待服務啟動
echo "⏳ 等待服務啟動（10秒）..."
sleep 10

# 檢查服務狀態
echo "📊 檢查服務狀態..."
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

# 健康檢查
echo "🏥 檢查服務健康狀態..."
sleep 5

if curl -f http://localhost:8081/api/v1/health &> /dev/null; then
    echo ""
    echo "✅ 服務重啟成功！"
    echo ""
    echo "📌 訪問地址："
    echo "   - API 健康檢查: http://localhost:8081/api/v1/health"
    echo "   - Swagger 文檔: http://localhost:8081/api/docs"
    echo ""
else
    echo "⚠️  健康檢查失敗，請查看日誌："
    if docker compose version &> /dev/null; then
        docker compose logs backend | tail -20
    else
        docker-compose logs backend | tail -20
    fi
    exit 1
fi

