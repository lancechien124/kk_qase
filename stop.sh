#!/bin/bash

# MeterSphere Python Backend - 停止腳本
# 從項目根目錄運行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend_python"

echo "🛑 MeterSphere Python Backend - 停止服務"
echo "========================================"

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    exit 1
fi

# 進入後端目錄
cd "${BACKEND_DIR}"

# 停止服務
echo "🐳 停止 Docker 服務..."
if docker compose version &> /dev/null; then
    docker compose down
else
    docker-compose down
fi

echo ""
echo "✅ 服務已停止"
echo ""
echo "💡 提示："
echo "   - 要刪除數據卷（會刪除所有數據），請使用: docker-compose down -v"
echo "   - 要重新啟動服務，請使用: ./run.sh"

