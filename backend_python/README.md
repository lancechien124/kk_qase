# MeterSphere Python Backend

MeterSphere Python 版本的後端實現，使用 FastAPI 構建。

## 特性

- 🚀 **FastAPI**: 現代化的 Python Web 框架，高性能
- 🔒 **JWT 認證**: 安全的用戶認證機制
- 🗄️ **異步數據庫**: 使用 SQLAlchemy Async 進行異步數據庫操作
- 📦 **模塊化設計**: 清晰的模塊結構，易於維護和擴展
- 🌍 **國際化支持**: 支持多語言（中文簡體/繁體、英文）
- 🤖 **AI 集成**: 支持 AI 生成測試用例和測試數據
- 📊 **測試框架**: 完整的單元測試和集成測試
- 📚 **完整文檔**: API 文檔、開發指南、部署指南

## 快速開始

### 使用 Docker Compose（推薦）

```bash
docker-compose up -d
```

### 本地開發

```bash
# 1. 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 2. 安裝依賴
pip install -r ../requirements.txt

# 3. 配置環境變量
cp .env.example .env
# 編輯 .env 文件

# 4. 初始化數據庫
alembic upgrade head

# 5. 運行服務
python main.py
```

服務將在 `http://localhost:8081` 啟動。

## 項目結構

```
backend_python/
├── app/                  # 應用代碼
│   ├── api/             # API 端點
│   ├── core/            # 核心功能
│   ├── models/           # 數據模型
│   ├── schemas/         # Pydantic 模式
│   ├── services/         # 業務邏輯
│   ├── tasks/           # Celery 任務
│   └── translations/    # 翻譯文件
├── alembic/             # 數據庫遷移
├── tests/               # 測試
├── docs/                # 文檔
└── main.py              # 應用入口
```

## 文檔

- [API 文檔](docs/API.md) - 完整的 API 參考文檔
- [開發指南](docs/DEVELOPMENT.md) - 開發環境設置和開發規範
- [部署指南](docs/DEPLOYMENT.md) - 生產環境部署指南
- [貢獻指南](docs/CONTRIBUTING.md) - 如何貢獻代碼

## API 文檔

開發環境下可以訪問：

- **Swagger UI**: `http://localhost:8081/api/docs`
- **ReDoc**: `http://localhost:8081/api/redoc`
- **OpenAPI JSON**: `http://localhost:8081/openapi.json`

## 測試

```bash
# 運行所有測試
pytest

# 運行單元測試
pytest tests/unit/

# 運行集成測試
pytest tests/integration/

# 帶覆蓋率報告
pytest --cov=app --cov-report=html
```

## 環境變量

主要環境變量配置（完整列表見 `.env.example`）：

```env
# 數據庫
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/metersphere

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 其他配置...
```

## 技術棧

- **Web 框架**: FastAPI
- **ORM**: SQLAlchemy (Async)
- **數據庫**: MySQL
- **緩存**: Redis
- **消息隊列**: Kafka
- **對象存儲**: MinIO
- **任務隊列**: Celery
- **測試**: pytest, pytest-asyncio
- **文檔**: Swagger/OpenAPI

## 主要功能

### 已實現

- ✅ 用戶認證和授權（JWT）
- ✅ 用戶管理
- ✅ 項目管理
- ✅ API 測試（定義、用例、場景）
- ✅ 功能用例管理
- ✅ 測試計劃管理
- ✅ 缺陷管理
- ✅ 文件管理（MinIO）
- ✅ 數據導入導出（Excel, XMind, Postman, Swagger, JMeter）
- ✅ JMeter 整合
- ✅ AI 功能（用例生成、測試數據生成）
- ✅ 國際化（i18n）
- ✅ 權限管理（RBAC）
- ✅ 速率限制
- ✅ 請求驗證

### 進行中

- 🔄 測試覆蓋率提升
- 🔄 更多 API 端點測試
- 🔄 性能優化

## 開發

請參考 [開發指南](docs/DEVELOPMENT.md) 了解詳細的開發說明。

## 部署

請參考 [部署指南](docs/DEPLOYMENT.md) 了解生產環境部署方法。

## 貢獻

歡迎貢獻代碼！請參考 [貢獻指南](docs/CONTRIBUTING.md)。

## 許可證

GPL v3 - 詳見 [LICENSE](../LICENSE) 文件

## 相關鏈接

- [MeterSphere 主項目](https://github.com/metersphere/metersphere)
- [官方網站](https://metersphere.io)
- [文檔](https://metersphere.io/docs/)

## 支持

如有問題，請：

1. 查看 [文檔](docs/)
2. 搜索 [Issues](https://github.com/metersphere/metersphere/issues)
3. 創建新 Issue
