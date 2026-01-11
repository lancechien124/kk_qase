# API 文檔

## 概述

MeterSphere Python 版本提供完整的 RESTful API，支持測試管理、接口測試、缺陷管理等功能。

## 基礎信息

- **Base URL**: `http://localhost:8081/api/v1`
- **API 版本**: v1
- **認證方式**: Bearer Token (JWT)
- **內容類型**: `application/json`

## 認證

大部分 API 端點需要認證。認證方式：

1. 通過 `/api/v1/auth/login` 端點登錄獲取 access_token
2. 在後續請求的 Header 中添加：`Authorization: Bearer <access_token>`

### 登錄示例

```bash
curl -X POST "http://localhost:8081/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password123"
```

響應：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## API 端點

### 認證 (Auth)

#### 登錄
- **POST** `/api/v1/auth/login`
- **描述**: 用戶登錄，獲取 access token
- **請求體**:
  ```json
  {
    "username": "user@example.com",
    "password": "password123"
  }
  ```
- **響應**: 
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

#### 獲取當前用戶
- **GET** `/api/v1/auth/me`
- **描述**: 獲取當前登錄用戶信息
- **認證**: 需要
- **響應**:
  ```json
  {
    "id": "user-id",
    "name": "User Name",
    "email": "user@example.com",
    "status": "active"
  }
  ```

#### 登出
- **POST** `/api/v1/auth/logout`
- **描述**: 用戶登出
- **認證**: 需要

### 用戶管理 (Users)

#### 獲取用戶列表
- **GET** `/api/v1/users?skip=0&limit=10`
- **描述**: 獲取用戶列表
- **認證**: 需要
- **查詢參數**:
  - `skip`: 跳過數量（默認: 0）
  - `limit`: 返回數量（默認: 10）

#### 獲取用戶詳情
- **GET** `/api/v1/users/{user_id}`
- **描述**: 獲取指定用戶詳情
- **認證**: 需要

#### 創建用戶
- **POST** `/api/v1/users`
- **描述**: 創建新用戶
- **認證**: 需要
- **請求體**:
  ```json
  {
    "name": "New User",
    "email": "newuser@example.com",
    "password": "password123"
  }
  ```

#### 更新用戶
- **PUT** `/api/v1/users/{user_id}`
- **描述**: 更新用戶信息
- **認證**: 需要
- **請求體**:
  ```json
  {
    "name": "Updated Name",
    "email": "updated@example.com"
  }
  ```

#### 刪除用戶
- **DELETE** `/api/v1/users/{user_id}`
- **描述**: 刪除用戶
- **認證**: 需要

### 项目管理 (Projects)

#### 獲取項目列表
- **GET** `/api/v1/project?skip=0&limit=10`
- **描述**: 獲取項目列表
- **認證**: 需要

#### 獲取項目詳情
- **GET** `/api/v1/project/{project_id}`
- **描述**: 獲取指定項目詳情
- **認證**: 需要

#### 創建項目
- **POST** `/api/v1/project`
- **描述**: 創建新項目
- **認證**: 需要
- **請求體**:
  ```json
  {
    "name": "New Project",
    "description": "Project description",
    "organization_id": "org-id"
  }
  ```

#### 更新項目
- **PUT** `/api/v1/project/{project_id}`
- **描述**: 更新項目信息
- **認證**: 需要

#### 刪除項目
- **DELETE** `/api/v1/project/{project_id}`
- **描述**: 刪除項目
- **認證**: 需要

### API 測試 (API Test)

#### 獲取 API 定義列表
- **GET** `/api/v1/api-test/definitions?project_id={project_id}`
- **描述**: 獲取 API 定義列表
- **認證**: 需要

#### 創建 API 定義
- **POST** `/api/v1/api-test/definitions`
- **描述**: 創建新的 API 定義
- **認證**: 需要
- **請求體**:
  ```json
  {
    "name": "Get User API",
    "method": "GET",
    "path": "/api/users/{id}",
    "project_id": "project-id"
  }
  ```

#### 執行 API 測試
- **POST** `/api/v1/api-test/execute`
- **描述**: 執行 API 測試
- **認證**: 需要

### 功能用例 (Functional Cases)

#### 獲取用例列表
- **GET** `/api/v1/case?project_id={project_id}`
- **描述**: 獲取功能用例列表
- **認證**: 需要

#### 創建用例
- **POST** `/api/v1/case`
- **描述**: 創建新的功能用例
- **認證**: 需要

### 測試計劃 (Test Plans)

#### 獲取測試計劃列表
- **GET** `/api/v1/test-plan?project_id={project_id}`
- **描述**: 獲取測試計劃列表
- **認證**: 需要

#### 創建測試計劃
- **POST** `/api/v1/test-plan`
- **描述**: 創建新的測試計劃
- **認證**: 需要

#### 執行測試計劃
- **POST** `/api/v1/test-plan/{plan_id}/execute`
- **描述**: 執行測試計劃
- **認證**: 需要

### 缺陷管理 (Bug Management)

#### 獲取缺陷列表
- **GET** `/api/v1/bug?project_id={project_id}`
- **描述**: 獲取缺陷列表
- **認證**: 需要

#### 創建缺陷
- **POST** `/api/v1/bug`
- **描述**: 創建新的缺陷
- **認證**: 需要

### 文件管理 (Files)

#### 上傳文件
- **POST** `/api/v1/files/upload`
- **描述**: 上傳文件到 MinIO
- **認證**: 需要
- **請求**: multipart/form-data
  - `file`: 文件
  - `folder`: 文件夾路徑（可選）

#### 下載文件
- **GET** `/api/v1/files/download/{file_path}`
- **描述**: 下載文件
- **認證**: 需要

#### 刪除文件
- **DELETE** `/api/v1/files/delete/{file_path}`
- **描述**: 刪除文件
- **認證**: 需要

### 國際化 (i18n)

#### 獲取當前語言
- **GET** `/api/v1/i18n/locale`
- **描述**: 獲取當前語言設置
- **認證**: 需要

#### 設置語言
- **POST** `/api/v1/i18n/locale?locale=zh_CN`
- **描述**: 設置語言
- **認證**: 需要
- **查詢參數**:
  - `locale`: 語言代碼（zh_CN, zh_TW, en_US）

#### 獲取翻譯
- **GET** `/api/v1/i18n/translations?locale=zh_CN`
- **描述**: 獲取所有翻譯
- **認證**: 需要

## 錯誤碼

### HTTP 狀態碼

- `200 OK` - 請求成功
- `201 Created` - 資源創建成功
- `400 Bad Request` - 請求參數錯誤
- `401 Unauthorized` - 未授權，需要登錄
- `403 Forbidden` - 無權限訪問
- `404 Not Found` - 資源不存在
- `409 Conflict` - 資源衝突
- `422 Unprocessable Entity` - 請求格式正確但語義錯誤
- `500 Internal Server Error` - 服務器內部錯誤

### 錯誤響應格式

```json
{
  "detail": "錯誤描述信息"
}
```

### 常見錯誤

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Swagger UI

開發環境下可以訪問 Swagger UI 查看完整的 API 文檔：

- **Swagger UI**: `http://localhost:8081/api/docs`
- **ReDoc**: `http://localhost:8081/api/redoc`
- **OpenAPI JSON**: `http://localhost:8081/openapi.json`

## 速率限制

API 有速率限制：
- 每用戶每 60 秒最多 100 個請求
- 超過限制會返回 `429 Too Many Requests`

## 版本控制

API 使用 URL 路徑進行版本控制：
- 當前版本: `/api/v1/`
- 未來版本: `/api/v2/`

## 支持

如有問題，請參考：
- [開發文檔](DEVELOPMENT.md)
- [部署指南](DEPLOYMENT.md)
- [GitHub Issues](https://github.com/metersphere/metersphere/issues)

