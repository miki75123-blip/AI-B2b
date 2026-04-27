# 📤 上傳到 GitHub 指南

## 方式一：使用上傳腳本（推薦）

### 步驟 1：重新打開終端

**重要：需要重新打開終端窗口**，Git 才能識別。

按 `Win + X` → 選擇 **Windows PowerShell** 或 **終端**

### 步驟 2：運行上傳腳本

```bash
cd c:/Users/akinp/WorkBuddy/20260427091307/ai-leadgen-agent
.\upload-to-github.bat
```

---

## 方式二：手動命令

### 步驟 1：在 GitHub 創建倉庫

1. 訪問 https://github.com 並登入
2. 點擊右上角 **+** → **New repository**
3. 填寫：
   - Repository name: `ai-leadgen-agent`
   - Description: `AI B2B Lead Generation System`
   - 選擇 **Private**
4. 點擊 **Create repository**
5. **複製** 頁面上顯示的 URL（類似 `https://github.com/您的用戶名/ai-leadgen-agent.git`）

### 步驟 2：在本地運行命令

重新打開終端，依次運行：

```bash
cd c:/Users/akinp/WorkBuddy/20260427091307/ai-leadgen-agent

git init
git add .
git commit -m "AI LeadGen Agent - Initial commit"
git branch -M main
git remote add origin https://github.com/您的用戶名/ai-leadgen-agent.git
git push -u origin main
```

### 步驟 3：輸入 GitHub 認證

第一次上傳需要認證，選擇：
- **HTTPS** 方式：輸入用戶名和 Personal Access Token

---

## 方式三：使用 GitHub網頁上傳

如果命令太複雜：

1. 訪問 https://github.com 並登入
2. 點擊 **+** → **New repository**
3. 倉庫名：`ai-leadgen-agent`
4. **不要** 勾選 "Add a README"
5. 點擊 **Create repository**
6. 頁面會顯示 "push an existing repository"，選擇第二個選項
7. 複製命令並在終端運行

---

## 🎯 下一步

上傳完成後，我可以幫您：
1. 一鍵部署到 Vercel + Railway
2. 獲得公開 URL

---

## 常見問題

### Q: 出現 "permission denied"？
需要創建 Personal Access Token：
1. GitHub → Settings → Developer settings
2. Personal access tokens → Generate new token
3. 勾選 `repo` 權限
4. 複製 token 代替密碼使用

### Q: 如何確認上傳成功？
訪問 `https://github.com/您的用戶名/ai-leadgen-agent`，能看到代碼就是成功。
