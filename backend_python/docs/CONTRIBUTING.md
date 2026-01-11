# 貢獻指南

感謝您對 MeterSphere Python 版本的關注！我們歡迎各種形式的貢獻。

## 如何貢獻

### 報告問題

如果您發現了 bug 或有功能建議，請：

1. 檢查 [Issues](https://github.com/metersphere/metersphere/issues) 確認問題尚未被報告
2. 創建新 Issue，包含：
   - 問題描述
   - 重現步驟
   - 預期行為
   - 實際行為
   - 環境信息（Python 版本、操作系統等）

### 提交代碼

#### 1. Fork 項目

在 GitHub 上 Fork 本項目到您的帳號。

#### 2. 克隆您的 Fork

```bash
git clone https://github.com/your-username/metersphere.git
cd metersphere/backend_python
```

#### 3. 創建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

#### 4. 進行更改

- 遵循代碼風格規範（見 [開發指南](DEVELOPMENT.md)）
- 添加必要的測試
- 更新相關文檔

#### 5. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修復問題描述"
```

提交信息格式：
- `feat:` - 新功能
- `fix:` - Bug 修復
- `docs:` - 文檔更新
- `style:` - 代碼格式（不影響功能）
- `refactor:` - 重構
- `test:` - 測試相關
- `chore:` - 構建過程或輔助工具的變動

#### 6. 推送更改

```bash
git push origin feature/your-feature-name
```

#### 7. 創建 Pull Request

在 GitHub 上創建 Pull Request，包含：
- 清晰的標題和描述
- 相關 Issue 編號（如果適用）
- 測試結果截圖或說明

## 代碼規範

### Python 代碼風格

- 遵循 PEP 8
- 使用類型提示（Type Hints）
- 函數和類添加文檔字符串

### 代碼示例

```python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

class MyService:
    """服務類的簡短描述"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化服務
        
        Args:
            db: 數據庫會話
        """
        self.db = db
    
    async def get_item(self, item_id: str) -> Optional[dict]:
        """
        獲取項目
        
        Args:
            item_id: 項目 ID
        
        Returns:
            項目字典，如果不存在則返回 None
        """
        # 實現邏輯
        pass
```

### 測試要求

- 新功能必須包含測試
- 測試覆蓋率不應低於 70%
- 確保所有測試通過

### 文檔要求

- 更新相關 API 文檔
- 更新 README（如果需要）
- 添加代碼註釋

## 審查流程

1. **自動檢查**: CI/CD 會自動運行測試和代碼檢查
2. **代碼審查**: 維護者會審查您的 PR
3. **反饋**: 根據反饋進行修改
4. **合併**: 審查通過後合併到主分支

## 開發環境設置

請參考 [開發指南](DEVELOPMENT.md) 設置開發環境。

## 行為準則

### 我們的承諾

為了營造開放和友好的環境，我們承諾：

- 尊重所有貢獻者
- 接受建設性批評
- 專注於對社區最有利的事情
- 對其他社區成員表示同理心

### 不可接受的行為

- 使用性別化的語言或評論
- 人身攻擊、侮辱性/貶損性評論
- 公開或私下騷擾
- 發布他人的私人信息
- 其他在專業環境中被認為不合適的行為

## 問題分類

### Bug 報告

使用 `bug` 標籤，包含：
- 問題描述
- 重現步驟
- 預期行為
- 實際行為
- 環境信息

### 功能請求

使用 `enhancement` 標籤，包含：
- 功能描述
- 使用場景
- 預期效果

### 文檔改進

使用 `documentation` 標籤，包含：
- 文檔位置
- 改進建議
- 具體內容

## 獲取幫助

如果您需要幫助：

1. 查看 [文檔](../README.md)
2. 搜索 [Issues](https://github.com/metersphere/metersphere/issues)
3. 創建新 Issue 詢問

## 許可證

通過貢獻，您同意您的貢獻將在與項目相同的許可證（GPL v3）下發布。

## 致謝

感謝所有為 MeterSphere 做出貢獻的開發者！

