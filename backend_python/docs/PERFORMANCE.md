# 性能優化指南

## 概述

本文檔介紹 MeterSphere Python 版本的性能優化功能和最佳實踐。

## 數據庫優化

### 索引優化

已為所有主要表添加了性能索引，包括：

- **單列索引**: 常用查詢字段（如 `email`, `project_id`, `deleted`）
- **複合索引**: 常見查詢組合（如 `project_id + deleted`）

運行遷移以應用索引：

```bash
alembic upgrade head
```

### 查詢優化

使用 `QueryOptimizer` 優化查詢：

```python
from app.core.database_optimization import QueryOptimizer

# 優化查詢
optimized_query = QueryOptimizer.optimize_select_query(
    query,
    limit=10,
    offset=0,
)

# 優化計數查詢
count = await QueryOptimizer.get_count_optimized(db, query, use_approximate=False)
```

### 連接池優化

配置連接池設置：

```python
from app.core.database_optimization import ConnectionPoolOptimizer

pool_settings = ConnectionPoolOptimizer.get_optimized_pool_settings(
    min_size=10,
    max_size=100,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)
```

## 緩存優化

### 查詢結果緩存

使用 `QueryCache` 緩存查詢結果：

```python
from app.core.cache import QueryCache

# 緩存查詢結果
result = await QueryCache.get_cached_query(
    cache_key="users:list:0:10",
    query_func=get_users_from_db,
    ttl=300,  # 5 minutes
    skip=0,
    limit=10,
)
```

### 緩存裝飾器

使用 `@cache_result` 裝飾器自動緩存函數結果：

```python
from app.core.cache import cache_result

@cache_result(ttl=3600, key_prefix="user")
async def get_user_by_id(user_id: str):
    # Function implementation
    pass
```

### 緩存失效

手動失效緩存：

```python
from app.core.cache import QueryCache

# 失效單個緩存
await QueryCache.invalidate_cache("user:123")

# 失效模式匹配的緩存
await QueryCache.invalidate_pattern("user:*")
```

## 分頁優化

### 使用分頁工具

```python
from app.utils.pagination import PaginationParams, PaginatedResponse

# 在 API 端點中使用
pagination = PaginationParams(page=1, page_size=10)

# 使用 PaginationHelper
from app.core.database_optimization import PaginationHelper

result = await PaginationHelper.paginate(
    db,
    query,
    page=1,
    page_size=10,
)
```

### 分頁響應

```python
return PaginatedResponse(
    items=result["items"],
    total=result["total"],
    page=result["page"],
    page_size=result["page_size"],
    pages=result["pages"],
)
```

## 批量操作

### 批量獲取

```python
from app.utils.batch_operations import BatchProcessor

processor = BatchProcessor(batch_size=100)

# 批量獲取用戶
users = await processor.batch_get(get_user_func, user_ids)
```

### 批量創建

```python
# 批量創建用戶
users = await processor.batch_create(create_user_func, user_data_list)
```

### 批量更新

```python
# 批量更新用戶
updates = {"user1": {"name": "New Name"}, "user2": {"email": "new@example.com"}}
users = await processor.batch_update(update_user_func, updates)
```

### 批量刪除

```python
# 批量刪除用戶
deleted_count = await processor.batch_delete(delete_user_func, user_ids)
```

### 批量插入

```python
from app.utils.batch_operations import BulkInsert

# 批量插入
inserted_count = await BulkInsert.bulk_insert(
    db,
    User,
    user_data_list,
    batch_size=1000,
)
```

## API 優化

### 分頁 API

使用優化的分頁端點：

```bash
GET /api/v1/users/paginated?page=1&page_size=10
```

響應包含完整的分頁信息：

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "pages": 10,
  "has_next": true,
  "has_previous": false
}
```

### 批量操作 API

使用批量操作端點減少請求次數：

```bash
# 批量獲取用戶
POST /api/v1/batch/users/batch-get
{
  "ids": ["user1", "user2", "user3"]
}

# 批量創建用戶
POST /api/v1/batch/users/batch-create
{
  "items": [
    {"name": "User1", "email": "user1@example.com"},
    {"name": "User2", "email": "user2@example.com"}
  ]
}

# 批量刪除用戶
POST /api/v1/batch/users/batch-delete
{
  "ids": ["user1", "user2"]
}
```

## 異步處理

所有服務層方法都使用 `async/await` 進行異步處理，避免阻塞：

```python
# 異步數據庫操作
result = await self.db.execute(query)

# 異步緩存操作
cached_value = await redis_client.get_cache(key)

# 並行執行多個操作
results = await asyncio.gather(
    get_user(user_id1),
    get_user(user_id2),
    get_user(user_id3),
)
```

## 性能監控

### 查詢性能

記錄慢查詢：

```python
import time
from app.core.logging import logger

start_time = time.time()
result = await db.execute(query)
elapsed = time.time() - start_time

if elapsed > 1.0:  # 超過 1 秒
    logger.warning(f"Slow query detected: {elapsed:.2f}s")
```

### 緩存命中率

監控緩存命中率：

```python
from app.core.cache import QueryCache

# 記錄緩存統計
cache_hits = 0
cache_misses = 0

# 在 QueryCache 中添加統計邏輯
```

## 最佳實踐

### 1. 使用索引

確保常用查詢字段都有索引：

```sql
CREATE INDEX idx_project_org_deleted ON project(organization_id, deleted);
```

### 2. 避免 N+1 查詢

使用 `selectinload` 或 `joinedload` 預加載關聯：

```python
from sqlalchemy.orm import selectinload

query = select(Project).options(selectinload(Project.organization))
```

### 3. 使用緩存

對頻繁查詢但不經常變更的數據使用緩存：

```python
# 項目列表緩存 5 分鐘
@cache_result(ttl=300, key_prefix="project")
async def get_projects():
    pass
```

### 4. 批量操作

對於多個操作，使用批量 API 而不是多個單獨請求：

```python
# 不好：多個請求
for user_id in user_ids:
    await get_user(user_id)

# 好：批量請求
users = await batch_get_users(user_ids)
```

### 5. 分頁查詢

避免一次性加載大量數據，使用分頁：

```python
# 不好：加載所有數據
all_users = await get_all_users()

# 好：分頁加載
users = await get_users_paginated(page=1, page_size=10)
```

### 6. 連接池配置

根據應用負載調整連接池大小：

```python
# 生產環境建議
DATABASE_POOL_SIZE=100
DATABASE_POOL_MIN_SIZE=10
DATABASE_POOL_MAX_OVERFLOW=20
```

## 性能測試

### 基準測試

使用 pytest-benchmark 進行性能測試：

```python
import pytest

@pytest.mark.benchmark
async def test_get_users_performance(benchmark, db_session):
    service = UserService(db_session)
    result = benchmark(service.get_users, skip=0, limit=10)
    assert len(result) <= 10
```

### 負載測試

使用工具如 Locust 或 JMeter 進行負載測試。

## 監控指標

建議監控以下指標：

- **響應時間**: API 端點響應時間
- **數據庫查詢時間**: 慢查詢監控
- **緩存命中率**: Redis 緩存效率
- **連接池使用率**: 數據庫連接池狀態
- **內存使用**: 應用內存使用情況
- **CPU 使用率**: CPU 負載

## 故障排查

### 慢查詢

1. 檢查是否有適當的索引
2. 使用 `EXPLAIN` 分析查詢計劃
3. 優化查詢語句

### 緩存問題

1. 檢查 Redis 連接
2. 驗證緩存鍵格式
3. 檢查緩存 TTL 設置

### 連接池問題

1. 檢查連接池大小配置
2. 監控連接池使用率
3. 檢查是否有連接洩漏

## 相關文檔

- [開發指南](DEVELOPMENT.md)
- [部署指南](DEPLOYMENT.md)
- [API 文檔](API.md)

