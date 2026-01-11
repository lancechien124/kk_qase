#!/bin/bash

# MeterSphere Python Backend - 啟動腳本
# 從項目根目錄運行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend_python"

echo "🚀 MeterSphere Python Backend - 啟動服務"
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

# 檢查 .env 文件
if [ ! -f .env ]; then
    echo "📝 創建 .env 文件..."
    cat > .env << 'EOF'
# Application
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=mysql+pymysql://root:password@mysql:3306/metersphere?charset=utf8mb4
MYSQL_ROOT_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Security (生產環境必須修改)
SECRET_KEY=change-this-secret-key-in-production
JWT_SECRET_KEY=change-this-jwt-secret-key-in-production
EOF
    echo "⚠️  已創建 .env 文件，生產環境請修改 SECRET_KEY 和 JWT_SECRET_KEY"
fi

# 啟動服務
echo "🐳 啟動 Docker 服務..."
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

# 等待服務啟動
echo "⏳ 等待服務啟動（30秒）..."
sleep 30

# 檢查服務狀態
echo "📊 檢查服務狀態..."
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

# 初始化數據庫
echo "🗄️  初始化數據庫..."
if docker compose version &> /dev/null; then
    docker compose exec -T backend python -m alembic upgrade head || echo "⚠️  數據庫遷移可能需要更多時間，請稍後重試"
else
    docker-compose exec -T backend python -m alembic upgrade head || echo "⚠️  數據庫遷移可能需要更多時間，請稍後重試"
fi

# 健康檢查
echo "🏥 檢查服務健康狀態..."
sleep 5

if curl -f http://localhost:8081/api/v1/health &> /dev/null; then
    echo ""
    echo "✅ 服務啟動成功！"
    echo ""
    echo "📌 訪問地址："
    echo "   - API 健康檢查: http://localhost:8081/api/v1/health"
    echo "   - Swagger 文檔: http://localhost:8081/api/docs"
    echo "   - ReDoc 文檔:   http://localhost:8081/api/redoc"
    echo ""
    echo "📝 常用命令："
    echo "   - 查看日誌: ./logs.sh 或 docker-compose -f backend_python/docker-compose.yml logs -f"
    echo "   - 停止服務: ./stop.sh"
    echo "   - 重啟服務: ./restart.sh"
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

