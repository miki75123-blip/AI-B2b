# AI Agent 系統架構

## 概述

AI LeadGen Agent 包含四個核心 AI Agent，它們協同工作以實現全自動的 B2B 潛在客戶開發。

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI LeadGen Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Scout Agent │───▶│  Writer Agent│───▶│ Sender Agent │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                                      │                 │
│         │                                      │                 │
│         ▼                                      ▼                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Optimizer Agent                        │   │
│  │              (持續學習與策略優化)                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Scout Agent

### 功能
- 從 eSources.co.uk、Creoate.com、TheWholesaler.co.uk 自動爬取供應商資訊
- 使用 Playwright 進行瀏覽器自動化
- 使用 BeautifulSoup 解析 HTML
- 數據驗證和質量評分

### 核心類

```python
class ScoutAgent:
    def scrape_esources(self, url: str) -> List[Dict]
    def scrape_creoate(self, url: str) -> List[Dict]
    def scrape_thewholesaler(self, url: str) -> List[Dict]
    def verify_supplier(self, supplier: Supplier) -> Dict
    def validate_email(self, email: str) -> bool
```

### 爬蟲策略

1. **頁面導航**：從首頁進入分類頁面
2. **列表提取**：解析供應商卡片資訊
3. **詳情頁**：進一步爬取詳細資訊
4. **速率限制**：每個頁面間隔 2 秒
5. **錯誤重試**：最多重試 3 次

## 2. Writer Agent

### 功能
- 分析供應商產品和業務資訊
- 使用 OpenAI GPT-4 生成個性化郵件
- 模板引擎支持變量替換
- A/B 測試變體生成
- 主題行優化

### 核心類

```python
class WriterAgent:
    def generate_personalized_email(
        self,
        template: EmailTemplate,
        supplier: Supplier,
        campaign: Campaign
    ) -> Dict[str, str]
    
    def generate_ab_variant(
        self,
        template: EmailTemplate,
        supplier: Supplier
    ) -> Dict[str, str]
    
    def analyze_product(self, description: str) -> Dict
    def optimize_timing(self, supplier: Supplier) -> Dict
```

### AI 提示詞策略

1. **角色定位**：專業 B2B 銷售郵件撰寫專家
2. **價值導向**：突出能為客戶帶來的價值
3. **個性化**：根據供應商特徵定制內容
4. **避免模板化**：確保每封郵件獨特自然

## 3. Sender Agent

### 功能
- SendGrid API 集成
- 郵件發送追蹤（開啟、點擊、退信）
- Webhook 處理
- 退訂管理
- 郵箱預熱策略

### 核心類

```python
class SenderAgent:
    def send_email(
        self,
        email_record: Email,
        sendgrid_api_key: str
    ) -> Dict
    
    def process_webhook(self, event_data: Dict) -> Dict
    def warmup_account(self, user: User) -> Dict
    def check_bounce_rate(self, user_id: int) -> Dict
```

### 發送策略

1. **預熱階段**：逐漸增加發送量
2. **頻率控制**：遵守每日和總量限制
3. **追蹤像素**：監控郵件開啟
4. **鏈接追蹤**：監控點擊行為

## 4. Optimizer Agent

### 功能
- 分析郵件效能數據
- 識別成功模式
- 生成優化建議
- 自動應用最佳實踐
- 持續學習改進

### 核心類

```python
class OptimizerAgent:
    def analyze_performance(self) -> Dict
    def generate_suggestions(self, analysis: Dict) -> List[Dict]
    def learn_from_campaign(self, campaign: Campaign) -> List[Dict]
    def apply_pattern(self, pattern: LearningPattern) -> bool
    def predict_success_rate(self, supplier: Supplier, template: EmailTemplate) -> float
```

### 學習模式

| 類型 | 觸發條件 | 策略 |
|------|---------|------|
| subject_optimization | 打開率 < 20% | 測試不同主題行 |
| timing_optimization | 不同時區表現差異 | 調整發送時間 |
| content_optimization | 點擊率 < 5% | 優化內容和 CTA |

## Celery 任務調度

### 任務列表

```python
# 爬蟲任務
scrape_suppliers_task - 爬取供應商
verify_supplier_task - 驗證單個供應商
batch_verify_suppliers_task - 批量驗證

# 郵件任務
send_email_task - 發送單封郵件
batch_send_emails_task - 批量發送
process_webhook_task - 處理 Webhook
warmup_email_accounts - 郵箱預熱

# 活動任務
run_campaign_task - 運行活動
check_and_process_campaigns - 檢查並處理活動

# 優化任務
run_daily_optimization - 每日優化
learn_from_campaign_task - 從活動學習
generate_optimization_report_task - 生成報告
```

### 定時調度

- **每日**：運行優化、分析活動數據、郵箱預熱
- **每小時**：檢查並處理運行中的活動

## 數據流向

```
1. Scout Agent 爬取
   └──▶ Supplier 表 (待驗證)

2. Scout Agent 驗證
   └──▶ Supplier 表 (已驗證/無效)

3. Writer Agent 生成
   └──▶ Email 表 (待發送)

4. Sender Agent 發送
   └──▶ Email 表 (已發送)

5. Webhook 回調
   └──▶ Email 表 (已開啟/已點擊/已退信)

6. Optimizer Agent 分析
   └──▶ LearningPattern 表 (學習模式)
```

## 性能優化

### 並發控制
- Celery Worker 數量可配置
- 郵件發送速率限制
- 爬蟲請求延遲

### 緩存策略
- Redis 緩存 API 響應
- 數據庫連接池

### 監控
- Flower 實時監控 Celery 任務
- 日誌集中管理
- 錯誤追蹤 (Sentry)
