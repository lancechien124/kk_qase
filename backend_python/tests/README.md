# 測試文檔

## 測試結構

```
tests/
├── conftest.py          # Pytest 配置和 fixtures
├── unit/                # 單元測試
│   ├── test_auth_service.py
│   ├── test_user_service.py
│   └── test_i18n.py
└── integration/         # 集成測試
    ├── test_auth_api.py
    ├── test_users_api.py
    └── test_project_api.py
```

## 運行測試

### 運行所有測試

```bash
pytest
```

### 運行單元測試

```bash
pytest tests/unit/
```

### 運行集成測試

```bash
pytest tests/integration/
```

### 運行特定測試文件

```bash
pytest tests/unit/test_auth_service.py
```

### 運行特定測試函數

```bash
pytest tests/unit/test_auth_service.py::test_create_user
```

### 帶覆蓋率報告

```bash
pytest --cov=app --cov-report=html
```

生成的 HTML 報告在 `htmlcov/index.html`

### 只運行標記的測試

```bash
pytest -m unit
pytest -m integration
```

## 測試標記

- `@pytest.mark.unit` - 單元測試
- `@pytest.mark.integration` - 集成測試
- `@pytest.mark.slow` - 慢速測試
- `@pytest.mark.auth` - 認證相關測試
- `@pytest.mark.api` - API 端點測試

## Fixtures

### `db_session`
創建測試數據庫會話，每個測試函數都會創建新的會話。

### `client`
創建未認證的測試客戶端。

### `authenticated_client`
創建已認證的測試客戶端。

### `test_user`
創建測試用戶。

### `admin_user`
創建管理員測試用戶。

### `test_project`
創建測試項目。

## 編寫測試

### 單元測試示例

```python
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test user creation"""
    auth_service = AuthService(db_session)
    
    user = await auth_service.create_user(
        name="test_user",
        email="test@example.com",
        password="test_password123",
    )
    
    assert user is not None
    assert user.name == "test_user"
```

### 集成測試示例

```python
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "test_password123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
```

## 測試覆蓋率目標

目標覆蓋率：80%+

查看覆蓋率報告：
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

