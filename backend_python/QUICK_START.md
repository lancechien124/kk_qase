# MeterSphere Python Backend - 快速啟動指南

## 🚀 使用 Docker Compose 啟動（推薦）

這是最簡單的方式，會自動啟動所有依賴服務（MySQL、Redis、Kafka、MinIO等）。

### 1. 準備環境變量

```bash
cd backend_python
cp .env.example .env
# 編輯 .env 文件，根據需要修改配置
```

### 2. 啟動所有服務

```bash
# 構建並啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f backend
```

### 3. 初始化數據庫

```bash
# 運行數據庫遷移
docker-compose exec backend python -m alembic upgrade head
```

### 4. 訪問服務

- **API**: http://localhost:8081
- **Swagger UI**: http://localhost:8081/api/docs
- **健康檢查**: http://localhost:8081/api/v1/health

### 5. 停止服務

```bash
# 停止所有服務
docker-compose down

# 停止並刪除數據卷（會刪除數據）
docker-compose down -v
```

---

## 🐳 使用 Docker 單獨運行

如果只需要運行後端服務，可以使用 Docker 單獨運行。

### 1. 構建鏡像

```bash
cd backend_python
docker build -t metersphere-python:latest .
```

### 2. 運行容器

```bash
docker run -d \
  --name metersphere-backend \
  -p 8081:8081 \
  -e DATABASE_URL=mysql+pymysql://user:password@host:3306/metersphere \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-secret-key \
  metersphere-python:latest
```

---

## 💻 本地開發環境運行

### 1. 系統要求

- Python 3.11+
- MySQL 8.0+
- Redis 6.0+
- Kafka (可選)
- MinIO (可選)

### 2. 安裝依賴

```bash
cd backend_python

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r ../requirements.txt
```

### 3. 配置環境變量

```bash
cp .env.example .env
# 編輯 .env 文件
```

### 4. 初始化數據庫

```bash
# 確保 MySQL 正在運行
# 創建數據庫
mysql -u root -p -e "CREATE DATABASE metersphere CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 運行遷移
alembic upgrade head
```

### 5. 啟動服務

```bash
# 使用 run.sh 腳本
./run.sh

# 或直接運行
python main.py
```

---

## 📋 完整部署步驟（Docker Compose）

### 步驟 1: 克隆項目

```bash
git clone <repository-url>
cd metersphere/backend_python
```

### 步驟 2: 配置環境變量

```bash
cp .env.example .env
```

編輯 `.env` 文件，至少修改以下關鍵配置：

```env
# 生產環境建議修改
SECRET_KEY=your-strong-random-secret-key
JWT_SECRET_KEY=your-strong-random-jwt-secret-key
DEBUG=False
LOG_LEVEL=INFO

# 數據庫密碼
DATABASE_URL=mysql+pymysql://root:your-password@mysql:3306/metersphere?charset=utf8mb4

# Redis 密碼（如果需要）
REDIS_PASSWORD=your-redis-password
```

### 步驟 3: 啟動服務

```bash
# 構建並啟動
docker-compose up -d --build

# 查看啟動日誌
docker-compose logs -f
```

### 步驟 4: 等待服務就緒

```bash
# 檢查健康狀態
curl http://localhost:8081/api/v1/health

# 或使用瀏覽器訪問
# http://localhost:8081/api/v1/health
```

### 步驟 5: 初始化數據庫

```bash
# 運行數據庫遷移
docker-compose exec backend python -m alembic upgrade head

# 驗證數據庫
docker-compose exec backend python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 步驟 6: 創建初始用戶（可選）

```bash
# 進入容器
docker-compose exec backend python

# 在 Python 交互環境中
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.database import AsyncSessionLocal
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        user_service = UserService(db)
        user = await user_service.create_user(
            name="admin",
            email="admin@example.com",
            password="admin123",
            create_user="system"
        )
        print(f"Admin user created: {user.id}")

asyncio.run(create_admin())
```

---

## 🔧 常用命令

### Docker Compose 命令

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 查看日誌
docker-compose logs -f backend

# 查看服務狀態
docker-compose ps

# 進入容器
docker-compose exec backend bash

# 執行命令
docker-compose exec backend python -m alembic upgrade head
```

### 數據庫遷移

```bash
# 創建新遷移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 應用遷移
docker-compose exec backend alembic upgrade head

# 回滾遷移
docker-compose exec backend alembic downgrade -1
```

### 備份和恢復

```bash
# 備份
./scripts/backup.sh

# 恢復
./scripts/restore.sh database_20240101_120000
```

---

## 🐛 故障排查

### 1. 服務無法啟動

```bash
# 檢查日誌
docker-compose logs backend

# 檢查端口是否被占用
lsof -i :8081

# 檢查 Docker 容器狀態
docker-compose ps
```

### 2. 數據庫連接失敗

```bash
# 檢查 MySQL 容器
docker-compose logs mysql

# 測試數據庫連接
docker-compose exec backend python -c "from app.core.database import async_engine; import asyncio; asyncio.run(async_engine.connect())"
```

### 3. Redis 連接失敗

```bash
# 檢查 Redis 容器
docker-compose logs redis

# 測試 Redis 連接
docker-compose exec backend python -c "from app.core.redis import redis_client; import asyncio; asyncio.run(redis_client.connect())"
```

### 4. 健康檢查失敗

```bash
# 檢查健康狀態
curl http://localhost:8081/api/v1/health

# 查看詳細健康信息
curl http://localhost:8081/api/v1/metrics
```

---

## 📝 生產環境部署

### 使用生產環境配置

```bash
# 使用生產環境 docker-compose
docker-compose -f docker-compose.prod.yml up -d

# 或使用部署腳本
./scripts/deploy.sh production
```

### 環境變量配置

生產環境建議設置：

```env
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=<強隨機字符串>
JWT_SECRET_KEY=<強隨機字符串>
DATABASE_URL=mysql+pymysql://user:password@host:3306/metersphere
REDIS_URL=redis://host:6379/0
REDIS_PASSWORD=<強密碼>
CORS_ORIGINS=https://your-domain.com
```

---

## 🔗 相關文檔

- [部署指南](docs/DEPLOYMENT.md) - 詳細的部署說明
- [開發指南](docs/DEVELOPMENT.md) - 開發環境設置
- [API 文檔](docs/API.md) - 完整的 API 參考
- [監控指南](docs/MONITORING.md) - 監控和日誌配置

---

## ✅ 驗證安裝

運行驗證腳本確認所有模組正常：

```bash
docker-compose exec backend python scripts/verify.py
```

或本地運行：

```bash
python3 scripts/verify.py
```

---

## 🎉 完成！

如果一切正常，您應該能夠：

1. ✅ 訪問 API: http://localhost:8081/api/v1/health
2. ✅ 查看 Swagger 文檔: http://localhost:8081/api/docs
3. ✅ 所有服務健康檢查通過

現在可以開始使用 MeterSphere Python Backend 了！

