# 🚀 快速啟動指南

## Windows 用戶

雙擊 `start.bat` 或在終端中運行：

```bash
start.bat
```

## Linux/macOS 用戶

```bash
chmod +x start.sh
./start.sh
```

## 手動啟動

### 1. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 填入 API Keys
```

必須配置的項目：
- `OPENAI_API_KEY` - OpenAI API 密鑰
- `SENDGRID_API_KEY` - SendGrid API 密鑰

### 2. 啟動 Docker

```bash
docker-compose up -d
```

### 3. 等待服務就緒

```bash
# 檢查狀態
docker-compose ps

# 查看日誌
docker-compose logs -f backend
```

### 4. 訪問服務

| 服務 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| API | http://localhost:8000/docs |
| Flower | http://localhost:5555 |

## 本地開發模式

### 後端

```bash
cd backend

# 安裝依賴
pip install -r requirements.txt

# 初始化數據庫
alembic upgrade head

# 啟動服務
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend

npm install
npm run dev
```

## 常見問題

### Q: Docker 啟動失敗？
```bash
# 重啟 Docker Desktop
docker-compose down
docker-compose up -d
```

### Q: 端口衝突？
```bash
# 檢查端口使用
netstat -ano | findstr "5432 6379 8000 5173"
```

### Q: 數據庫遷移失敗？
```bash
docker-compose exec backend alembic upgrade head
```

## 停止服務

```bash
docker-compose down
```
