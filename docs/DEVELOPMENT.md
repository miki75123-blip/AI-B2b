# AI LeadGen Agent

## 開發環境設置

### 1. 克隆與配置

```bash
# 複製環境變數
cp .env.example .env

# 編輯 .env 填入您的 API Keys
```

### 2. Docker 環境（推薦）

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f backend
```

### 3. 本地開發

#### 後端

```bash
cd backend

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 運行測試
pytest

# 啟動服務
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安裝依賴
npm install

# 運行開發服務器
npm run dev

# 構建生產版本
npm run build
```

## 服務說明

### 後端 API
- 地址: http://localhost:8000
- API 文檔: http://localhost:8000/docs

### 前端
- 地址: http://localhost:5173
- 自動熱重載

### PostgreSQL
- 地址: localhost:5432
- 默認用戶: postgres
- 默認密碼: postgres

### Redis
- 地址: localhost:6379

### Celery Worker
- 處理異步任務（爬蟲、郵件發送等）

## 常用命令

```bash
# 運行測試
docker-compose exec backend pytest

# 查看 Celery 任務
docker-compose exec backend celery -A app.tasks.celery_app inspect active

# 重啟服務
docker-compose restart backend

# 清理並重建
docker-compose down -v
docker-compose up -d --build
```

## 開發規範

### 代碼風格
- 使用 TypeScript 類型提示
- 遵循 ESLint 和 Prettier 配置
- 提交前運行 lint 和格式化

### 提交規範
```
feat: 新功能
fix: 修復 bug
docs: 文檔更新
style: 代碼格式
refactor: 重構
test: 測試相關
chore: 構建或工具
```

## 故障排除

### 端口衝突
```bash
# 檢查端口使用
netstat -tulpn | grep 8000
```

### 數據庫遷移
```bash
docker-compose exec backend alembic upgrade head
```

### 清除緩存
```bash
docker-compose exec redis redis-cli FLUSHALL
```
