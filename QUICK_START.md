# KK QASE - 快速開始指南

## 🚀 最簡單的方式（推薦）

從項目根目錄運行：

```bash
# 啟動所有服務
./run.sh

# 停止服務
./stop.sh

# 重啟服務
./restart.sh

# 查看日誌
./logs.sh
```

## 📋 詳細步驟

### 1. 環境要求

- Docker & Docker Compose
- 或 Python 3.11+, MySQL 8.0+, Redis 6.0+

### 2. 使用 Docker Compose（推薦）

```bash
# 進入項目目錄
cd kk_qase

# 運行啟動腳本
./run.sh
```

腳本會自動：
- ✅ 檢查 Docker 環境
- ✅ 創建 .env 文件（如果不存在）
- ✅ 構建並啟動所有服務
- ✅ 初始化數據庫
- ✅ 驗證服務健康狀態

### 3. 訪問服務

啟動成功後，訪問：

- **API 文檔**: http://localhost:8081/api/docs
- **健康檢查**: http://localhost:8081/api/v1/health
- **ReDoc 文檔**: http://localhost:8081/api/redoc

### 4. 本地開發（可選）

```bash
cd backend_python
pip install -r ../requirements.txt
cp .env.example .env
# 編輯 .env 文件
python main.py
```

## 📝 更多信息

- [README.md](README.md) - 項目總覽
- [使用說明.md](使用說明.md) - 詳細使用說明
- [backend_python/運行指南.md](backend_python/運行指南.md) - 完整運行指南
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 項目結構說明
