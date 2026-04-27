# AI LeadGen Agent

全自動 AI B2B 潛在客戶開發系統

## 功能特性

- 🤖 **Scout Agent**: 自動從多個 B2B 平台爬取供應商資訊
- ✍️ **Writer Agent**: AI 生成個性化銷售郵件
- 📧 **Sender Agent**: 智能郵件發送與追蹤
- 📊 **Optimizer Agent**: 持續優化策略提升效果
- 📈 **Dashboard**: 美觀的 Web 監控面板

## 快速開始

### 前置需求

- Docker & Docker Compose
- Node.js 18+ (本地開發)
- Python 3.11+ (本地開發)

### 啟動服務

```bash
# 複製環境變數配置
cp .env.example .env

# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 本地開發

```bash
# 後端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 項目結構

```
ai-leadgen-agent/
├── backend/              # FastAPI 後端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 數據庫模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── services/    # 業務邏輯
│   │   ├── agents/      # AI Agent 實現
│   │   └── tasks/       # Celery 任務
│   └── tests/           # 測試
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/ # UI 組件
│   │   ├── pages/      # 頁面
│   │   ├── hooks/      # 自定義 Hooks
│   │   ├── services/   # API 服務
│   │   └── stores/     # 狀態管理
│   └── public/
├── docker/              # Docker 配置
├── nginx/               # Nginx 配置
├── docs/                # 文檔
└── docker-compose.yml   # Docker Compose 配置
```

## 技術棧

- **前端**: React 18, TypeScript, Vite, TailwindCSS, Shadcn/ui
- **後端**: FastAPI, SQLAlchemy, PostgreSQL, Redis
- **爬蟲**: Playwright, BeautifulSoup
- **AI**: OpenAI GPT-4
- **任務隊列**: Celery, Redis
- **郵件**: SendGrid API
- **部署**: Docker Compose, Nginx

## API 文檔

啟動服務後訪問:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 許可證

MIT License
"" 
