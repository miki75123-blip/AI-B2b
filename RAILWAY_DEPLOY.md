# 🚀 Railway 部署配置指南

## 問題修復

本項目已配置正確的 Railway 部署設定。

### 已修復的問題

❌ **問題**：`start.sh` 在 Railway 環境中執行會導致 "Docker not found" 錯誤
✅ **解決**：已刪除 `start.sh`，創建 `railway.toml` 配置

---

## 部署步驟

### 1. 確保 railway.toml 存在

項目根目錄已有 `railway.toml`，配置如下：

```toml
[build]
builder = "docker"
dockerfilePath = "docker/Dockerfile.backend"

[deploy]
startCommand = "cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"
```

### 2. Railway 項目設置

1. 登入 https://railway.app
2. 選擇您的 `ai-leadgen-agent` 項目
3. 點擊 **Settings** → **Build & Deploy**
4. 確認設置：
   - **Builder**: Docker
   - **Dockerfile**: `docker/Dockerfile.backend`

### 3. 環境變數

在 Railway 中設置必要的環境變數：

| 變數名 | 值 | 說明 |
|--------|-----|------|
| `OPENAI_API_KEY` | 您的 API Key | 必填 |
| `SECRET_KEY` | 隨機字符串 | 用於 JWT 認證 |
| `DATABASE_URL` | PostgreSQL 連接字串 | Railway 自動提供 |

### 4. 重新部署

1. 點擊 **Deployments** 標籤
2. 點擊右上角 **Redeploy** 按鈕
3. 等待構建完成

---

## 驗證部署

部署成功後，訪問：
- API URL: `https://您的項目名.up.railway.app`
- API 文檔: `https://您的項目名.up.railway.app/docs`

---

## 常見問題

### Q: 仍然出現 "Docker not found" 錯誤？

確保 Railway 項目的 Start Command 為空，讓 `railway.toml` 控制啟動命令。

### Q: 如何查看部署日誌？

在 Railway 的 **Deployments** 頁面，點擊具體的部署記錄查看日誌。

### Q: 數據庫連接失敗？

確保 `DATABASE_URL` 環境變數已正確設置，格式為：
```
postgresql://用戶名:密碼@主機:端口/數據庫名
```
