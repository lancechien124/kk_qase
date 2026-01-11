# 開發指南

## 環境要求

- Python 3.10+
- MySQL 5.7+ 或 8.0+
- Redis 6.0+
- Kafka 2.8+ (可選)
- MinIO (可選)

## 快速開始

### 1. 克隆項目

```bash
git clone https://github.com/metersphere/metersphere.git
cd metersphere/backend_python
```

### 2. 創建虛擬環境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安裝依賴

```bash
pip install -r ../requirements.txt
```

### 4. 配置環境變量

創建 `.env` 文件：

```env
# 數據庫配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/metersphere?charset=utf8mb4

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# Kafka 配置
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False
MINIO_BUCKET=metersphere

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI 配置（可選）
AI_ENABLED=False
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1

# JMeter 配置
JMETER_HOME=/opt/jmeter
```

### 5. 初始化數據庫

```bash
# 運行遷移
alembic upgrade head
```

### 6. 運行開發服務器

```bash
python main.py
```

服務器將在 `http://localhost:8081` 啟動。

## 項目結構

```
backend_python/
├── app/
│   ├── api/              # API 端點
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/             # 核心功能（配置、數據庫、安全等）
│   ├── models/           # 數據庫模型
│   ├── schemas/          # Pydantic 模式
│   ├── services/         # 業務邏輯層
│   ├── tasks/            # Celery 任務
│   ├── translations/     # 翻譯文件
│   └── utils/            # 工具函數
├── alembic/              # 數據庫遷移
├── tests/                # 測試
├── docs/                 # 文檔
├── main.py               # 應用入口
├── requirements.txt      # 依賴列表
└── pytest.ini           # 測試配置
```

## 開發規範

### 代碼風格

- 使用 Python 3.10+ 特性
- 遵循 PEP 8 代碼風格
- 使用類型提示（Type Hints）
- 使用 async/await 進行異步操作

### 命名規範

- **文件**: 使用小寫字母和下劃線（`snake_case`）
- **類**: 使用大駝峰（`PascalCase`）
- **函數/變量**: 使用小寫字母和下劃線（`snake_case`）
- **常量**: 使用大寫字母和下劃線（`UPPER_SNAKE_CASE`）

### 目錄結構規範

- **API 端點**: `app/api/v1/endpoints/`
- **服務層**: `app/services/`
- **數據模型**: `app/models/`
- **Schema**: `app/schemas/`
- **工具函數**: `app/utils/`

## 添加新功能

### 1. 創建數據模型

在 `app/models/` 中創建模型：

```python
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin

class MyModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "my_model"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
```

### 2. 創建 Schema

在 `app/schemas/` 中創建 Pydantic 模式：

```python
from pydantic import BaseModel

class MyModelCreate(BaseModel):
    name: str
    description: Optional[str] = None

class MyModelResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
```

### 3. 創建服務

在 `app/services/` 中創建服務：

```python
from sqlalchemy.ext.asyncio import AsyncSession

class MyModelService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: MyModelCreate):
        # 實現創建邏輯
        pass
```

### 4. 創建 API 端點

在 `app/api/v1/endpoints/` 中創建端點：

```python
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=MyModelResponse)
async def create_model(
    data: MyModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MyModelService(db)
    return await service.create(data)
```

### 5. 註冊路由

在 `app/api/v1/__init__.py` 中註冊：

```python
from app.api.v1.endpoints import my_model

api_router.include_router(my_model.router, prefix="/my-model", tags=["我的模型"])
```

### 6. 創建數據庫遷移

```bash
alembic revision --autogenerate -m "Add my_model table"
alembic upgrade head
```

## 測試

### 運行測試

```bash
# 運行所有測試
pytest

# 運行單元測試
pytest tests/unit/

# 運行集成測試
pytest tests/integration/

# 帶覆蓋率
pytest --cov=app --cov-report=html
```

### 編寫測試

參考 `tests/` 目錄中的示例測試。

## 調試

### 日誌

使用 Loguru 進行日誌記錄：

```python
from app.core.logging import logger

logger.info("Info message")
logger.error("Error message", exc_info=True)
```

### 開發模式

設置 `DEBUG=True` 在 `.env` 中啟用調試模式：

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 數據庫遷移

### 創建遷移

```bash
alembic revision --autogenerate -m "描述"
```

### 應用遷移

```bash
alembic upgrade head
```

### 回滾遷移

```bash
alembic downgrade -1
```

## 代碼檢查

### Linting

```bash
# 使用 flake8（如果安裝）
flake8 app/

# 使用 pylint（如果安裝）
pylint app/
```

### 格式化

```bash
# 使用 black（如果安裝）
black app/

# 使用 isort（如果安裝）
isort app/
```

## 常見問題

### 數據庫連接失敗

檢查 `.env` 中的 `DATABASE_URL` 配置是否正確。

### Redis 連接失敗

確保 Redis 服務正在運行，檢查 `REDIS_URL` 配置。

### 端口被占用

修改 `main.py` 中的 `PORT` 設置或 `.env` 中的 `PORT` 環境變量。

## 貢獻

請參考 [CONTRIBUTING.md](CONTRIBUTING.md) 了解貢獻指南。

