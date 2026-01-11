# KK QASE 項目結構說明

## 📁 目錄結構

```
kk_qase/
├── backend/                    # Java 後端（原版 MeterSphere）
│   ├── app/                    # 應用主模組
│   ├── framework/              # 框架層
│   └── services/               # 業務服務層
│
├── backend_python/            # Python 後端（推薦使用）
│   ├── app/                    # 應用代碼
│   │   ├── api/               # API 端點
│   │   │   └── v1/
│   │   │       └── endpoints/  # 17 個 API 端點模組
│   │   ├── services/          # 服務層（18 個服務）
│   │   ├── models/            # 數據模型（14 個模型）
│   │   ├── schemas/           # Pydantic 模式定義
│   │   ├── core/              # 核心模組
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 數據庫連接
│   │   │   ├── security.py    # 安全認證
│   │   │   ├── redis.py       # Redis 連接
│   │   │   ├── kafka.py       # Kafka 連接
│   │   │   └── minio.py       # MinIO 連接
│   │   ├── utils/             # 工具函數
│   │   └── tasks/             # 異步任務
│   ├── alembic/               # 數據庫遷移
│   ├── tests/                 # 測試套件
│   ├── docs/                  # 文檔
│   ├── scripts/               # 部署腳本
│   ├── Dockerfile             # Docker 構建文件
│   ├── docker-compose.yml     # Docker Compose 配置
│   └── requirements.txt       # Python 依賴
│
├── frontend/                   # Vue.js 前端
│   ├── src/
│   │   ├── api/               # API 調用
│   │   ├── components/       # 組件
│   │   ├── views/            # 頁面視圖
│   │   └── ...
│   └── package.json
│
├── run.sh                      # 啟動腳本
├── stop.sh                     # 停止腳本
├── restart.sh                  # 重啟腳本
├── logs.sh                     # 日誌查看腳本
├── README.md                   # 項目說明
├── PR.md                       # 改動說明
└── 使用說明.md                 # 使用說明
```

## 🎯 核心模組說明

### Python 後端 (`backend_python/`)

#### API 端點 (`app/api/v1/endpoints/`)
- `auth.py` - 認證相關（登錄、註冊、刷新 Token）
- `users.py` - 用戶管理
- `api_test.py` - API 測試
- `bug_management.py` - 缺陷管理
- `case_management.py` - 用例管理
- `project_management.py` - 項目管理
- `test_plan.py` - 測試計劃
- `files.py` - 文件管理
- `import_export.py` - 導入導出
- `jmeter.py` - JMeter 執行
- `ai.py` - AI 功能
- `i18n.py` - 國際化
- `health.py` - 健康檢查
- 等共 17 個模組

#### 服務層 (`app/services/`)
- `auth_service.py` - 認證服務
- `user_service.py` - 用戶服務
- `api_test_service.py` - API 測試服務
- `bug_management_service.py` - 缺陷管理服務
- `case_management_service.py` - 用例管理服務
- `project_service.py` - 項目服務
- `test_plan_service.py` - 測試計劃服務
- `file_service.py` - 文件服務
- `jmeter_service.py` - JMeter 服務
- `ai_service.py` - AI 服務
- 等共 18 個服務

#### 數據模型 (`app/models/`)
- `user.py` - 用戶模型
- `organization.py` - 組織模型
- `project.py` - 項目模型
- `api_test.py` - API 測試模型
- `functional_case.py` - 功能用例模型
- `test_plan.py` - 測試計劃模型
- `bug.py` - 缺陷模型
- 等共 14 個模型

#### 核心模組 (`app/core/`)
- `config.py` - 配置管理（Pydantic Settings）
- `database.py` - 數據庫連接（SQLAlchemy Async）
- `security.py` - 安全認證（JWT, BCrypt）
- `redis.py` - Redis 連接和緩存
- `kafka.py` - Kafka 消息隊列
- `minio.py` - MinIO 對象存儲
- `rate_limit.py` - API 限流中間件
- `i18n.py` - 國際化支持
- `metrics.py` - 監控指標收集
- `logging.py` - 日誌系統

## 🚀 快速開始

### 使用 Docker Compose（推薦）

```bash
# 從項目根目錄
./run.sh
```

### 本地開發

```bash
cd backend_python
pip install -r ../requirements.txt
python main.py
```

## 📝 文檔

- [README.md](README.md) - 項目總覽
- [使用說明.md](使用說明.md) - 使用指南
- [backend_python/運行指南.md](backend_python/運行指南.md) - 完整運行指南
- [backend_python/docs/](backend_python/docs/) - 詳細技術文檔

