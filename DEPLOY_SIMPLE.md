# 簡化部署到 Vercel

## 步驟 1：刪除舊項目
1. 進入 Vercel 舊項目
2. Settings → 最底部 → Delete Project

## 步驟 2：重新部署
1. 回到 https://vercel.com/new
2. 選擇 "AI-B2b" 倉庫
3. Framework Preset: Other
4. Root Directory: ./frontend
5. Build Command: npm run build
6. Deploy!

## 重要：只部署 frontend
- 這會部署純靜態前端
- API 功能需要另行配置後端
