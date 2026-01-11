# 監控與日誌指南

## 概述

本文檔介紹 MeterSphere Python 版本的監控和日誌功能。

## 健康檢查

### 健康檢查端點

應用提供多個健康檢查端點：

#### 1. 綜合健康檢查

```bash
GET /api/v1/health
```

返回所有服務的健康狀態：

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "3.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "minio": {
      "status": "healthy",
      "message": "MinIO connection successful"
    },
    "kafka": {
      "status": "healthy",
      "message": "Kafka producer available"
    }
  }
}
```

狀態說明：
- `healthy`: 所有關鍵服務正常
- `degraded`: 部分非關鍵服務異常
- `unhealthy`: 關鍵服務異常

#### 2. 就緒檢查（Kubernetes Readiness Probe）

```bash
GET /api/v1/health/ready
```

用於 Kubernetes 就緒探針，檢查服務是否準備好接收流量。

#### 3. 存活檢查（Kubernetes Liveness Probe）

```bash
GET /api/v1/health/live
```

用於 Kubernetes 存活探針，檢查服務是否仍在運行。

## 指標收集

### 應用指標

```bash
GET /api/v1/metrics
```

返回詳細的應用指標：

```json
{
  "timestamp": "2024-01-01T00:00:00",
  "application": {
    "name": "MeterSphere",
    "version": "3.0.0",
    "environment": "production",
    "uptime": 3600.0
  },
  "database": {
    "pool_size": 10,
    "checked_in": 8,
    "checked_out": 2,
    "overflow": 0
  },
  "redis": {
    "connected_clients": 5,
    "used_memory": 1048576,
    "used_memory_human": "1.00M",
    "keyspace_hits": 1000,
    "keyspace_misses": 100
  },
  "cache": {
    "hit_rate": 90.91,
    "hits": 1000,
    "misses": 100,
    "total_requests": 1100
  },
  "system": {
    "cpu_percent": 15.5,
    "memory_used_mb": 256.0,
    "memory_percent": 12.5,
    "num_threads": 10,
    "open_files": 50
  },
  "requests": {
    "request_count": 10000,
    "error_count": 50,
    "error_rate": 0.5,
    "avg_response_time": 0.125,
    "min_response_time": 0.010,
    "max_response_time": 2.500
  }
}
```

### Prometheus 指標

```bash
GET /api/v1/metrics/prometheus
```

返回 Prometheus 格式的指標：

```
metersphere_info{version="3.0.0",environment="prod"} 1
metersphere_database_pool_size 10
metersphere_database_pool_checked_in 8
metersphere_database_pool_checked_out 2
metersphere_redis_connected_clients 5
metersphere_redis_used_memory_bytes 1048576
metersphere_redis_keyspace_hits 1000
metersphere_redis_keyspace_misses 100
metersphere_cache_hit_rate 90.91
metersphere_cache_hits 1000
metersphere_cache_misses 100
metersphere_system_cpu_percent 15.5
metersphere_system_memory_used_bytes 268435456
metersphere_system_memory_percent 12.5
metersphere_system_threads 10
metersphere_requests_total 10000
metersphere_requests_errors_total 50
metersphere_requests_error_rate 0.5
metersphere_requests_avg_response_time_seconds 0.125
metersphere_requests_min_response_time_seconds 0.010
metersphere_requests_max_response_time_seconds 2.500
```

### Prometheus 配置

在 `prometheus.yml` 中添加：

```yaml
scrape_configs:
  - job_name: 'metersphere'
    scrape_interval: 15s
    metrics_path: '/api/v1/metrics/prometheus'
    static_configs:
      - targets: ['localhost:8000']
```

## 日誌系統

### 日誌配置

應用使用 `loguru` 進行日誌記錄，支持：

- **控制台輸出**: 彩色格式化日誌
- **文件輸出**: 按日期輪轉的日誌文件
- **結構化日誌**: JSON 格式的結構化日誌
- **錯誤日誌**: 單獨的錯誤日誌文件

### 日誌文件

日誌文件位於 `logs/` 目錄：

- `app_YYYY-MM-DD.log`: 應用日誌（所有級別）
- `structured_YYYY-MM-DD.log`: 結構化 JSON 日誌
- `error_YYYY-MM-DD.log`: 錯誤日誌（僅 ERROR 級別）

### 日誌輪轉

- **輪轉時間**: 每天午夜（00:00）
- **保留時間**: 30 天
- **壓縮**: 舊日誌自動壓縮為 ZIP

### 日誌級別

可通過環境變量 `LOG_LEVEL` 設置：

- `DEBUG`: 詳細調試信息
- `INFO`: 一般信息（默認）
- `WARNING`: 警告信息
- `ERROR`: 錯誤信息
- `CRITICAL`: 嚴重錯誤

### 結構化日誌

結構化日誌以 JSON 格式輸出，便於日誌分析工具處理：

```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "INFO",
  "message": "Request completed",
  "module": "app.core.metrics_middleware",
  "function": "dispatch",
  "line": 45,
  "method": "GET",
  "path": "/api/v1/users",
  "status_code": 200,
  "response_time": 0.125
}
```

### 請求日誌

所有 HTTP 請求都會自動記錄，包括：

- 請求方法
- 請求路徑
- 查詢參數
- 客戶端 IP
- 響應狀態碼
- 響應時間

### 錯誤日誌

錯誤和異常會記錄詳細信息：

- 異常類型
- 異常消息
- 完整堆棧跟踪

## 中間件

### MetricsMiddleware

自動追蹤請求指標：

- 請求計數
- 錯誤計數
- 響應時間統計（平均、最小、最大）

### StructuredLoggingMiddleware

自動記錄結構化請求日誌。

## 監控最佳實踐

### 1. 健康檢查

定期檢查健康狀態：

```bash
# 每 30 秒檢查一次
watch -n 30 curl http://localhost:8000/api/v1/health
```

### 2. 指標監控

使用 Prometheus 和 Grafana 進行可視化監控：

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'metersphere'
    scrape_interval: 15s
    metrics_path: '/api/v1/metrics/prometheus'
    static_configs:
      - targets: ['localhost:8000']
```

### 3. 日誌聚合

使用 ELK Stack 或 Loki 進行日誌聚合和分析：

```yaml
# promtail-config.yml
scrape_configs:
  - job_name: metersphere
    static_configs:
      - targets:
          - localhost
        labels:
          job: metersphere
          __path__: /path/to/logs/*.log
```

### 4. 告警規則

設置 Prometheus 告警規則：

```yaml
groups:
  - name: metersphere
    rules:
      - alert: HighErrorRate
        expr: metersphere_requests_error_rate > 5
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: HighResponseTime
        expr: metersphere_requests_avg_response_time_seconds > 1
        for: 5m
        annotations:
          summary: "High response time detected"
      
      - alert: ServiceDown
        expr: up{job="metersphere"} == 0
        for: 1m
        annotations:
          summary: "MeterSphere service is down"
```

### 5. Kubernetes 探針

在 Kubernetes 部署中使用健康檢查：

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 故障排查

### 檢查健康狀態

```bash
curl http://localhost:8000/api/v1/health
```

### 查看指標

```bash
curl http://localhost:8000/api/v1/metrics
```

### 查看日誌

```bash
# 查看應用日誌
tail -f logs/app_$(date +%Y-%m-%d).log

# 查看錯誤日誌
tail -f logs/error_$(date +%Y-%m-%d).log

# 查看結構化日誌
tail -f logs/structured_$(date +%Y-%m-%d).log | jq
```

### 常見問題

1. **健康檢查失敗**
   - 檢查數據庫連接
   - 檢查 Redis 連接
   - 檢查服務配置

2. **指標異常**
   - 檢查系統資源使用
   - 檢查數據庫連接池
   - 檢查緩存命中率

3. **日誌不輸出**
   - 檢查日誌目錄權限
   - 檢查日誌級別設置
   - 檢查磁盤空間

## 相關文檔

- [部署指南](DEPLOYMENT.md)
- [性能優化指南](PERFORMANCE.md)
- [開發指南](DEVELOPMENT.md)

