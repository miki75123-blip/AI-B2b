# 🖥️ 本地開發模式啟動指南

本指南適用於 **沒有 Docker** 的環境。

## 前置條件

- Python 3.10+
- Node.js 18+
- npm 9+

## 步驟 1：配置環境變數

```bash
cd c:/Users/akinp/WorkBuddy/20260427091307/ai-leadgen-agent

# 複製本地配置
copy .env.local .env
```

編輯 `.env` 文件，**必須**填入：
```
OPENAI_API_KEY=sk-your-openai-api-key
```

## 步驟 2：安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

> ⚠️ 如果遇到相依問題，嘗試：
> ```bash
> pip install --ignore-installed -r requirements.txt
> ```

## 步驟 3：初始化數據庫

```bash
cd backend
python init_db.py
```

成功後會看到：
```
✓ 數據庫表已創建
✓ 測試用戶已創建
  Email: admin@example.com
  Password: admin123
```

## 步驟 4：安裝前端依賴

```bash
# 新開一個終端
cd frontend
npm install
```

## 步驟 5：啟動服務

### 終端 1 - 後端
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 終端 2 - 前端
```bash
cd frontend
npm run dev
```

## 步驟 6：訪問

| 服務 | 地址 |
|------|------|
| 前端網站 | http://localhost:5173 |
| API 文檔 | http://localhost:8000/docs |

### 登入資訊
- Email: `admin@example.com`
- Password: `admin123`

---

## 🔧 常見問題

### Q: pip 安裝失敗？
```bash
# 升級 pip
python -m pip install --upgrade pip
```

### Q: 缺少 Microsoft Visual C++？
下載 Visual Studio Build Tools 或使用 Anaconda。

### Q: 端口被佔用？
```bash
# 查找佔用端口的進程
netstat -ano | findstr "8000"  # 或 5173
taskkill /PID <進程ID> /F
```

### Q: 想要使用 PostgreSQL？
修改 `.env` 中的 `DATABASE_URL`：
```
DATABASE_URL=postgresql://user:password@localhost:5432/leadgen
```

### Q: 想要使用真實郵件？
在 `.env` 中填入 SendGrid API Key：
```
SENDGRID_API_KEY=your-key-here
```
