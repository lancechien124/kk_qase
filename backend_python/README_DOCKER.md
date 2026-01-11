# 🐳 Docker 運行指南

## 快速開始（一鍵啟動）

```bash
# 1. 進入項目目錄
cd backend_python

# 2. 複製環境變量文件
cp .env.example .env

# 3. 啟動所有服務（包括 MySQL、Redis、Kafka、MinIO）
docker-compose up -d

# 4. 等待服務啟動（約 30 秒）
sleep 30

# 5. 初始化數據庫
docker-compose exec backend python -m alembic upgrade head

# 6. 檢查服務狀態
curl http://localhost:8081/api/v1/health
```

## 📋 詳細步驟

### 步驟 1: 準備環境

```bash
cd metersphere/backend_python
cp .env.example .env
```

### 步驟 2: 配置環境變量（可選）

編輯 `.env` 文件，修改以下關鍵配置：

```env
# 生產環境必須修改
SECRET_KEY=your-strong-random-secret-key-here
JWT_SECRET_KEY=your-strong-random-jwt-secret-key-here

# 數據庫密碼
MYSQL_ROOT_PASSWORD=your-secure-password

# 其他配置根據需要修改
```

### 步驟 3: 啟動服務

```bash
# 構建並啟動所有服務
docker-compose up -d --build

# 查看啟動日誌
docker-compose logs -f
```

### 步驟 4: 等待服務就緒

```bash
# 檢查所有服務狀態
docker-compose ps

# 應該看到所有服務都是 "Up" 狀態
```

### 步驟 5: 初始化數據庫

```bash
# 運行數據庫遷移
docker-compose exec backend python -m alembic upgrade head
```

### 步驟 6: 驗證安裝

```bash
# 檢查健康狀態
curl http://localhost:8081/api/v1/health

# 或使用瀏覽器訪問
# http://localhost:8081/api/v1/health
```

## 🌐 訪問服務

啟動成功後，可以訪問：

- **API 健康檢查**: http://localhost:8081/api/v1/health
- **Swagger 文檔**: http://localhost:8081/api/docs
- **ReDoc 文檔**: http://localhost:8081/api/redoc
- **指標端點**: http://localhost:8081/api/v1/metrics

## 🔧 常用命令

### 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看後端服務日誌
docker-compose logs -f backend

# 查看數據庫日誌
docker-compose logs -f mysql
```

### 重啟服務

```bash
# 重啟所有服務
docker-compose restart

# 重啟特定服務
docker-compose restart backend
```

### 停止服務

```bash
# 停止所有服務（保留數據）
docker-compose down

# 停止並刪除數據卷（會刪除所有數據）
docker-compose down -v
```

### 進入容器

```bash
# 進入後端容器
docker-compose exec backend bash

# 進入 MySQL 容器
docker-compose exec mysql bash

# 執行 Python 命令
docker-compose exec backend python -c "print('Hello')"
```

## 🗄️ 數據庫操作

### 運行遷移

```bash
# 應用所有遷移
docker-compose exec backend alembic upgrade head

# 創建新遷移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 回滾遷移
docker-compose exec backend alembic downgrade -1
```

### 數據庫備份

```bash
# 使用備份腳本
docker-compose exec backend ./scripts/backup.sh

# 或手動備份
docker-compose exec mysql mysqldump -u root -ppassword metersphere > backup.sql
```

## 🐛 故障排查

### 服務無法啟動

```bash
# 1. 檢查日誌
docker-compose logs backend

# 2. 檢查端口占用
lsof -i :8081
lsof -i :3306
lsof -i :6379

# 3. 檢查容器狀態
docker-compose ps
docker ps -a
```

### 數據庫連接失敗

```bash
# 檢查 MySQL 是否正常運行
docker-compose exec mysql mysqladmin ping -h localhost -u root -ppassword

# 檢查數據庫是否存在
docker-compose exec mysql mysql -u root -ppassword -e "SHOW DATABASES;"
```

### Redis 連接失敗

```bash
# 測試 Redis 連接
docker-compose exec redis redis-cli ping

# 應該返回: PONG
```

### 健康檢查失敗

```bash
# 查看詳細健康信息
curl http://localhost:8081/api/v1/health | jq

# 檢查各服務狀態
curl http://localhost:8081/api/v1/metrics | jq
```

## 📊 服務端口

| 服務 | 端口 | 說明 |
|------|------|------|
| Backend API | 8081 | 主應用服務 |
| MySQL | 3306 | 數據庫 |
| Redis | 6379 | 緩存 |
| Kafka | 9092 | 消息隊列 |
| Zookeeper | 2181 | Kafka 協調服務 |
| MinIO API | 9000 | 對象存儲 API |
| MinIO Console | 9001 | 對象存儲控制台 |

## 🔒 生產環境建議

### 1. 修改默認密碼

```env
MYSQL_ROOT_PASSWORD=strong-password-here
REDIS_PASSWORD=strong-password-here
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=strong-password-here
SECRET_KEY=strong-random-secret-key
JWT_SECRET_KEY=strong-random-jwt-secret-key
```

### 2. 使用生產環境配置

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 配置資源限制

在 `docker-compose.prod.yml` 中已配置資源限制，可根據實際需求調整。

### 4. 啟用 SSL/TLS

建議使用 Nginx 反向代理並配置 SSL 證書。

## 📝 環境變量說明

詳細環境變量說明請查看 `.env.example` 文件。

主要環境變量：

- `DATABASE_URL`: 數據庫連接字符串
- `REDIS_URL`: Redis 連接字符串
- `SECRET_KEY`: 應用密鑰（必須修改）
- `JWT_SECRET_KEY`: JWT 密鑰（必須修改）
- `DEBUG`: 調試模式（生產環境設為 False）
- `LOG_LEVEL`: 日誌級別

## ✅ 驗證安裝

運行驗證腳本：

```bash
docker-compose exec backend python scripts/verify.py
```

應該看到：

```
✓ All modules verified successfully!
```

## 🎉 完成！

如果所有步驟都成功，您現在應該能夠：

1. ✅ 訪問 API 健康檢查端點
2. ✅ 查看 Swagger API 文檔
3. ✅ 所有服務正常運行

開始使用 MeterSphere Python Backend！

