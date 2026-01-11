# 部署指南

## 部署方式

MeterSphere Python 版本支持多種部署方式：

1. Docker Compose（推薦）
2. Docker
3. 直接部署

## Docker Compose 部署（推薦）

### 1. 準備環境

確保已安裝：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 配置環境變量

編輯 `docker-compose.yml` 或創建 `.env` 文件：

```env
# 數據庫配置
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE=metersphere
MYSQL_USER=metersphere
MYSQL_PASSWORD=password

# Redis 配置
REDIS_PASSWORD=

# MinIO 配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

### 3. 啟動服務

```bash
docker-compose up -d
```

### 4. 初始化數據庫

```bash
# 進入容器
docker-compose exec backend python -m alembic upgrade head
```

### 5. 訪問服務

- API: `http://localhost:8081`
- Swagger UI: `http://localhost:8081/api/docs`

## Docker 部署

### 1. 構建鏡像

```bash
docker build -t metersphere-python:latest .
```

### 2. 運行容器

```bash
docker run -d \
  --name metersphere-python \
  -p 8081:8081 \
  -e DATABASE_URL=mysql+pymysql://user:password@host:3306/metersphere \
  -e REDIS_URL=redis://host:6379/0 \
  metersphere-python:latest
```

## 直接部署

### 1. 系統要求

- Ubuntu 20.04+ / CentOS 7+ / macOS
- Python 3.10+
- MySQL 5.7+ / 8.0+
- Redis 6.0+

### 2. 安裝依賴

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3-pip mysql-server redis-server

# CentOS/RHEL
sudo yum install python3.10 python3-pip mysql-server redis
```

### 3. 配置數據庫

```sql
CREATE DATABASE metersphere CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'metersphere'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON metersphere.* TO 'metersphere'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 配置 Redis

編輯 `/etc/redis/redis.conf`：

```conf
bind 127.0.0.1
port 6379
```

啟動 Redis：

```bash
sudo systemctl start redis
sudo systemctl enable redis
```

### 5. 部署應用

```bash
# 克隆項目
git clone https://github.com/metersphere/metersphere.git
cd metersphere/backend_python

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r ../requirements.txt

# 配置環境變量
cp .env.example .env
# 編輯 .env 文件

# 初始化數據庫
alembic upgrade head

# 運行應用
python main.py
```

### 6. 使用 systemd 管理服務

創建 `/etc/systemd/system/metersphere.service`：

```ini
[Unit]
Description=MeterSphere Python Backend
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/metersphere/backend_python
Environment="PATH=/opt/metersphere/backend_python/venv/bin"
ExecStart=/opt/metersphere/backend_python/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl daemon-reload
sudo systemctl start metersphere
sudo systemctl enable metersphere
```

## 生產環境配置

### 1. 環境變量

生產環境建議設置：

```env
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=<強隨機字符串>
DATABASE_URL=mysql+pymysql://user:password@host:3306/metersphere
REDIS_URL=redis://host:6379/0
```

### 2. 使用 Gunicorn

安裝 Gunicorn：

```bash
pip install gunicorn uvicorn[standard]
```

運行：

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8081 \
  --access-logfile - \
  --error-logfile -
```

### 3. 使用 Nginx 反向代理

創建 `/etc/nginx/sites-available/metersphere`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

啟用配置：

```bash
sudo ln -s /etc/nginx/sites-available/metersphere /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. SSL/TLS 配置

使用 Let's Encrypt：

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 監控和日誌

### 日誌位置

- 應用日誌: `/opt/metersphere/logs/`
- 系統日誌: `/var/log/metersphere/`

### 健康檢查

健康檢查端點：

```bash
curl http://localhost:8081/health
```

## 備份和恢復

### 數據庫備份

```bash
mysqldump -u metersphere -p metersphere > backup.sql
```

### 數據庫恢復

```bash
mysql -u metersphere -p metersphere < backup.sql
```

### MinIO 備份

```bash
# 使用 MinIO client
mc mirror minio/metersphere /backup/metersphere
```

## 擴展和優化

### 水平擴展

使用負載均衡器（如 Nginx）分發請求到多個實例。

### 數據庫優化

- 配置適當的連接池大小
- 添加必要的索引
- 定期優化表

### Redis 優化

- 配置適當的內存限制
- 啟用持久化（如果需要）

## 故障排查

### 檢查服務狀態

```bash
# Docker Compose
docker-compose ps

# systemd
sudo systemctl status metersphere

# 檢查日誌
docker-compose logs -f backend
# 或
sudo journalctl -u metersphere -f
```

### 常見問題

1. **數據庫連接失敗**: 檢查數據庫服務是否運行，配置是否正確
2. **Redis 連接失敗**: 檢查 Redis 服務是否運行
3. **端口被占用**: 檢查端口是否被其他服務占用
4. **權限問題**: 確保應用有足夠的權限訪問所需資源

## 升級

### 升級步驟

1. 備份數據庫和文件
2. 停止服務
3. 更新代碼
4. 運行數據庫遷移：`alembic upgrade head`
5. 重啟服務

```bash
# Docker Compose
docker-compose pull
docker-compose up -d
docker-compose exec backend alembic upgrade head

# 直接部署
git pull
source venv/bin/activate
pip install -r ../requirements.txt
alembic upgrade head
sudo systemctl restart metersphere
```

## 支持

如有問題，請參考：
- [開發文檔](DEVELOPMENT.md)
- [API 文檔](API.md)
- [GitHub Issues](https://github.com/metersphere/metersphere/issues)

