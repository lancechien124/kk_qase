# KK QASE - 開源測試管理平台

<p align="center">
  <img src="https://metersphere.oss-cn-hangzhou.aliyuncs.com/img/MeterSphere-%E7%B4%AB%E8%89%B2.png" alt="KK QASE" width="300" />
</p>
<h3 align="center">新一代的開源持續測試工具</h3>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html"><img src="https://shields.io/github/license/metersphere/metersphere?color=%231890FF" alt="License: GPL v3"></a>
</p>
<hr />

KK QASE 是基於 MeterSphere 的新一代開源持續測試工具，讓軟件測試工作更簡單、更高效，不再成為持續交付的瓶頸。

## ✨ 主要特性

-   **AI 賦能**：內置 AI 助手，支持 AI 生成功能用例、接口用例等，提升測試效率；
-   **測試管理**：從測試用例管理，到測試計劃執行、缺陷管理、測試報告生成，具有遠超 TestLink 等傳統測試管理工具的使用體驗；
-   **接口測試**：集 Postman 的易用與 JMeter 的靈活於一體，接口調試、接口定義、接口 Mock、場景自動化、接口報告，你想要的都有；
-   **團隊協作**：採用"系統-組織-項目"分層設計理念，幫助用戶擺脫單機測試工具的束縛，方便快捷地開展團隊協作；
-   **插件體系**：提供各種類別的插件，用戶可以按需取用，快速實現測試能力的擴展以及與 DevOps 流水線的集成。

## 🚀 快速開始

### 方式一：使用 Docker Compose（推薦）

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

### 方式二：本地開發環境

```bash
cd backend_python
pip install -r ../requirements.txt
cp .env.example .env
# 編輯 .env 文件配置資料庫等
python main.py
```

詳細說明請參考：
- [backend_python/README.md](backend_python/README.md)
- [backend_python/運行指南.md](backend_python/運行指南.md)
- [backend_python/快速啟動.md](backend_python/快速啟動.md)
- [使用說明.md](使用說明.md)

## 📋 技術棧

### Java 版本（原版）
-   後端: [Spring Boot](https://www.tutorialspoint.com/spring_boot/spring_boot_introduction.htm)
-   前端: [Vue.js](https://vuejs.org/)
-   中間件: [MySQL](https://www.mysql.com/), [Kafka](https://kafka.apache.org/), [MinIO](https://min.io/), [Redis](https://redis.com/)
-   基礎設施: [Docker](https://www.docker.com/)
-   測試引擎: [JMeter](https://jmeter.apache.org/)

### Python 版本（新增，推薦）

本專案現在也提供 Python 版本的後端實現，位於 `backend_python/` 目錄。

-   後端: [FastAPI](https://fastapi.tiangolo.com/) - 現代化的 Python Web 框架
-   前端: [Vue.js](https://vuejs.org/) (與 Java 版本共用)
-   ORM: [SQLAlchemy](https://www.sqlalchemy.org/) (Async) - 異步資料庫操作
-   中間件: [MySQL](https://www.mysql.com/), [Kafka](https://kafka.apache.org/), [MinIO](https://min.io/), [Redis](https://redis.com/)
-   任務調度: [Celery](https://docs.celeryq.dev/) - 替代 Quartz
-   基礎設施: [Docker](https://www.docker.com/)
-   測試引擎: [JMeter](https://jmeter.apache.org/)

## 📁 項目結構

```
kk_qase/
├── backend/              # Java 後端（原版）
├── backend_python/       # Python 後端（推薦）
│   ├── app/              # 應用代碼
│   │   ├── api/          # API 端點
│   │   ├── services/     # 服務層
│   │   ├── models/       # 數據模型
│   │   └── core/         # 核心模組
│   ├── tests/            # 測試套件
│   ├── docs/             # 文檔
│   └── scripts/          # 部署腳本
├── frontend/             # Vue.js 前端
├── run.sh                # 啟動腳本
├── stop.sh               # 停止腳本
├── restart.sh            # 重啟腳本
└── logs.sh               # 日誌查看腳本
```

## 🌐 訪問地址

啟動成功後，可以訪問：

- **API 文檔**: http://localhost:8081/api/docs
- **健康檢查**: http://localhost:8081/api/v1/health
- **ReDoc 文檔**: http://localhost:8081/api/redoc

## 📊 完成度

### Python 後端完成度
- ✅ **API 端點**: 17/17 (100%)
- ✅ **服務層**: 18/18 (100%)
- ✅ **核心模組**: 15/15 (100%)
- ✅ **數據模型**: 14/14 (100%)
- ✅ **總體完成度**: 98%

詳細信息請查看 [backend_python/SUMMARY.md](backend_python/SUMMARY.md)

## 🔧 開發

### 環境要求
- Python 3.11+
- MySQL 8.0+
- Redis 6.0+
- Docker & Docker Compose

### 開發指南
詳細開發指南請查看：
- [backend_python/docs/DEVELOPMENT.md](backend_python/docs/DEVELOPMENT.md)
- [backend_python/docs/API.md](backend_python/docs/API.md)

## 📝 文檔

- [使用說明](使用說明.md) - 快速使用指南
- [PR 說明](PR.md) - 項目改動說明
- [backend_python/運行指南.md](backend_python/運行指南.md) - 完整運行指南
- [backend_python/快速啟動.md](backend_python/快速啟動.md) - 快速啟動指南
- [backend_python/docs/](backend_python/docs/) - 詳細技術文檔

## 🤝 貢獻

歡迎貢獻代碼！請查看 [backend_python/docs/CONTRIBUTING.md](backend_python/docs/CONTRIBUTING.md) 了解貢獻指南。

## 📄 License

Copyright (c) 2014-2026 飞致云 FIT2CLOUD, All rights reserved.

Licensed under The GNU General Public License version 3 (GPLv3) (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

https://www.gnu.org/licenses/gpl-3.0.html

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
