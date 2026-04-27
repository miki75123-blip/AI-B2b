# 🚀 免費部署指南（15分鐘完成）

本指南幫助您將 AI LeadGen Agent 部署到網上，獲得公開 URL 訪問。

---

## 方案：Vercel 前端 + Railway 後端

### 費用：完全免費 ✅

| 服務 | 費用 | 功能 |
|------|------|------|
| Vercel | 免費 | 前端網站托管 |
| Railway | 免費（$5額度） | 後端 API + 數據庫 |
| 總計 | **免費** | 完整系統 |

---

## 步驟 1：申請帳號（5分鐘）

1. **GitHub** → https://github.com （必填）
2. **Vercel** → https://vercel.com （用 GitHub 登入）
3. **Railway** → https://railway.app （用 GitHub 登入）

---

## 步驟 2：上傳代碼到 GitHub（5分鐘）

### 2.1 在 GitHub 創建倉庫

1. 登入 https://github.com
2. 點擊右上角 **+** → **New repository**
3. 名稱填：`ai-leadgen-agent`
4. 選擇 **Private**（私人）
5. 點擊 **Create repository**

### 2.2 上傳代碼

在您的電腦終端運行：

```bash
cd c:/Users/akinp/WorkBuddy/20260427091307/ai-leadgen-agent

git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/您的用戶名/ai-leadgen-agent.git
git push -u origin main
```

---

## 步驟 3：部署後端到 Railway（5分鐘）

### 3.1 創建 Railway 項目

1. 登入 https://railway.app
2. 點擊 **New Project** → **Deploy from GitHub repo**
3. 選擇 `ai-leadgen-agent` 倉庫
4. Railway 會檢測為 **Python** 項目

### 3.2 配置環境變數

在 Railway 項目頁面，點擊 **Settings** → **Environment Variables**，添加：

| 變數名 | 值 |
|--------|-----|
| `OPENAI_API_KEY` | 您的 OpenAI API Key |
| `SECRET_KEY` | 隨機字符串（可用 https://randomkeygen.com 生成） |
| `DATABASE_URL` | 保持默認（Railway 會自動創建 PostgreSQL） |

### 3.3 部署

Railway 會自動：
- 安裝依賴
- 運行遷移
- 啟動服務

部署完成後，您會獲得一個 URL，如：`https://ai-leadgen-agent.up.railway.app`

---

## 步驟 4：部署前端到 Vercel（2分鐘）

### 4.1 連接倉庫

1. 登入 https://vercel.com
2. 點擊 **Add New** → **Project**
3. 導入 `ai-leadgen-agent` 倉庫
4. Vercel 會自動檢測為 Vite/React 項目

### 4.2 配置環境變數

點擊 **Environment Variables**，添加：

| 變數名 | 值 |
|--------|-----|
| `VITE_API_URL` | 您的 Railway URL（如：`https://ai-leadgen-agent.up.railway.app`） |

### 4.3 部署

點擊 **Deploy**！

完成後您會獲得一個 Vercel URL，如：`https://ai-leadgen-agent.vercel.app`

---

## 步驟 5：配置 API 地址

部署完成後：

1. 複製 Vercel 給您的 URL
2. 在 Railway 中，設置環境變數：
   ```
   CORS_ORIGINS=https://ai-leadgen-agent.vercel.app
   ```

---

## 🎉 完成！

現在您可以通過公開 URL 訪問系統：

| 服務 | URL |
|------|-----|
| **前端網站** | `https://ai-leadgen-agent.vercel.app` |
| **API** | `https://ai-leadgen-agent.up.railway.app` |

### 測試帳戶
- Email: `admin@example.com`
- Password: `admin123`

---

## 常見問題

### Q: Railway $5 免費用完怎麼辦？
Railway 提供 $5 免費額度，大約可用 1-2 個月。您可以：
- 升級到付費計劃
- 換用 Render.com（完全免費但較慢）
- 換用 Render 免費方案

### Q: 如何更新代碼？
```bash
git add .
git commit -m "update"
git push
```
Railway 和 Vercel 會自動重新部署。

### Q: 忘記密碼怎麼辦？
在 Railway 的 Shell 中運行：
```bash
python
from app.core.security import get_password_hash
print(get_password_hash("newpassword"))
```
然後手動更新數據庫。

---

## 備選方案：純本地使用

如果您只需要在本地電腦使用：

1. 雙擊 `OPEN.html` 打开
2. 確保後端和前端都在運行
3. 點擊按鈕訪問系統
