# 🚀 MeterSphere Python Backend - 運行指南

## 最簡單的方式：使用 Docker Compose（推薦）

### 一鍵啟動

```bash
cd backend_python
./start.sh
```

這個腳本會自動：
1. ✅ 檢查 Docker 和 Docker Compose
2. ✅ 創建 .env 文件（如果不存在）
3. ✅ 構建並啟動所有服務
4. ✅ 初始化數據庫
5. ✅ 驗證服務健康狀態

### 手動啟動步驟

#### 1. 準備環境變量

```bash
cd backend_python

# 創建 .env 文件（如果不存在）
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
```

#### 2. 啟動所有服務

```bash
# 構建並啟動
docker-compose up -d --build

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

#### 3. 等待服務就緒（約 30-60 秒）

```bash
# 檢查健康狀態
curl http://localhost:8081/api/v1/health

# 或使用瀏覽器訪問
# http://localhost:8081/api/v1/health
```

#### 4. 初始化數據庫

```bash
# 運行數據庫遷移
docker-compose exec backend python -m alembic upgrade head
```

#### 5. 驗證安裝

```bash
# 檢查 API 文檔
curl http://localhost:8081/api/docs

# 或瀏覽器訪問
# http://localhost:8081/api/docs
```

## 📋 完整命令列表

### 啟動和停止

```bash
# 啟動所有服務
docker-compose up -d

# 停止所有服務
docker-compose down

# 停止並刪除數據（會刪除所有數據）
docker-compose down -v

# 重啟服務
docker-compose restart

# 查看服務狀態
docker-compose ps
```

### 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看後端日誌
docker-compose logs -f backend

# 查看數據庫日誌
docker-compose logs -f mysql
```

### 數據庫操作

```bash
# 運行遷移
docker-compose exec backend python -m alembic upgrade head

# 創建新遷移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 進入數據庫
docker-compose exec mysql mysql -u root -ppassword metersphere
```

### 進入容器

```bash
# 進入後端容器
docker-compose exec backend bash

# 執行 Python 命令
docker-compose exec backend python -c "print('Hello')"
```

## 🌐 訪問地址

啟動成功後，可以訪問：

- **API 健康檢查**: http://localhost:8081/api/v1/health
- **Swagger 文檔**: http://localhost:8081/api/docs
- **ReDoc 文檔**: http://localhost:8081/api/redoc
- **指標端點**: http://localhost:8081/api/v1/metrics

## 🔧 服務端口

| 服務 | 端口 | 說明 |
|------|------|------|
| Backend API | 8081 | 主應用服務 |
| MySQL | 3306 | 數據庫 |
| Redis | 6379 | 緩存 |
| Kafka | 9092 | 消息隊列 |
| Zookeeper | 2181 | Kafka 協調 |
| MinIO API | 9000 | 對象存儲 |
| MinIO Console | 9001 | 對象存儲控制台 |

## 🐛 常見問題

### 1. 端口被占用

```bash
# 檢查端口占用
lsof -i :8081
lsof -i :3306

# 修改 docker-compose.yml 中的端口映射
```

### 2. 數據庫連接失敗

```bash
# 檢查 MySQL 容器
docker-compose logs mysql

# 等待 MySQL 完全啟動（約 30 秒）
sleep 30
docker-compose exec backend python -m alembic upgrade head
```

### 3. 服務無法啟動

```bash
# 查看詳細日誌
docker-compose logs backend

# 檢查容器狀態
docker-compose ps

# 重啟服務
docker-compose restart backend
```

### 4. 健康檢查失敗

```bash
# 手動檢查健康狀態
curl http://localhost:8081/api/v1/health

# 查看詳細錯誤
docker-compose exec backend python -c "from app.core.database import async_engine; import asyncio; asyncio.run(async_engine.connect())"
```

## 📝 生產環境部署

### 使用生產配置

```bash
# 使用生產環境配置
docker-compose -f docker-compose.prod.yml up -d

# 或使用部署腳本
./scripts/deploy.sh production
```

### 環境變量配置

生產環境必須修改：

```env
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=<強隨機字符串>
JWT_SECRET_KEY=<強隨機字符串>
MYSQL_ROOT_PASSWORD=<強密碼>
```

## ✅ 驗證運行

運行驗證腳本：

```bash
docker-compose exec backend python scripts/verify.py
```

應該看到：

```
✓ All modules verified successfully!
```

## 🎉 完成！

如果一切正常，您現在可以：

1. ✅ 訪問 API 文檔
2. ✅ 使用所有 API 端點
3. ✅ 所有服務正常運行

開始使用 MeterSphere Python Backend！

