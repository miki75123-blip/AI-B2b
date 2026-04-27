# AI LeadGen Agent - API 文檔

## 認證

所有 API 都需要 Bearer Token 認證。

```bash
curl -H "Authorization: Bearer <your_token>" https://api.example.com/api/...
```

## 認證 API

### 註冊用戶
```
POST /api/auth/register
```

**請求體：**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "User Name",
  "company_name": "Company Ltd"
}
```

### 登入
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password123
```

**響應：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 獲取當前用戶
```
GET /api/auth/me
```

## 供應商 API

### 列出供應商
```
GET /api/suppliers/?page=1&page_size=20&search=keyword
```

**響應：**
```json
{
  "items": [
    {
      "id": 1,
      "company_name": "ABC Trading Ltd",
      "email": "contact@abc.co.uk",
      "country": "UK",
      "verification_status": "verified",
      "quality_score": 85,
      "is_contacted": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 創建供應商
```
POST /api/suppliers/
```

**請求體：**
```json
{
  "company_name": "New Supplier Ltd",
  "email": "contact@newsupplier.com",
  "country": "UK",
  "business_type": "wholesaler"
}
```

### 爬取供應商
```
POST /api/suppliers/scrape?platform=esources
```

**平台選項：** `esources`, `creoate`, `thewholesaler`

## 活動 API

### 列出活動
```
GET /api/campaigns/
```

### 創建活動
```
POST /api/campaigns/
```

**請求體：**
```json
{
  "name": "UK Wholesalers Campaign",
  "description": "Target UK wholesale suppliers",
  "target_countries": ["UK", "United Kingdom"],
  "daily_send_limit": 50,
  "total_send_limit": 1000
}
```

### 啟動活動
```
POST /api/campaigns/{id}/start
```

### 暫停活動
```
POST /api/campaigns/{id}/pause
```

## 郵件 API

### 列出郵件模板
```
GET /api/emails/templates/
```

### 創建郵件模板
```
POST /api/emails/templates/
```

**請求體：**
```json
{
  "name": "Introduction Email",
  "subject_template": "{{supplier_name}} - Partnership Opportunity",
  "body_template": "<h1>Hello {{supplier_name}}</h1><p>...</p>",
  "is_default": true
}
```

**可用變量：**
- `{{supplier_name}}` - 供應商公司名稱
- `{{supplier_country}}` - 供應商所在國家
- `{{supplier_city}}` - 供應商所在城市
- `{{supplier_business_type}}` - 企業類型
- `{{campaign_name}}` - 活動名稱

## 儀表板 API

### 獲取儀表板數據
```
GET /api/dashboard/
```

**響應：**
```json
{
  "supplier_stats": {
    "total": 150,
    "verified": 120,
    "pending": 30
  },
  "email_stats": {
    "total_sent": 5000,
    "open_rate": 25.5,
    "click_rate": 5.2
  },
  "campaign_stats": {
    "total": 5,
    "active": 2
  }
}
```

## Webhook

### SendGrid Webhook
```
POST /api/webhooks/sendgrid
```

處理的事件：`delivered`, `open`, `click`, `bounce`, `unsubscribe`

```json
{
  "event": "open",
  "email": "recipient@example.com",
  "sg_message_id": "abc123"
}
```

## 錯誤響應

```json
{
  "detail": "Error message"
}
```

**HTTP 狀態碼：**
- 200 - 成功
- 201 - 創建成功
- 400 - 請求錯誤
- 401 - 未授權
- 403 - 權限不足
- 404 - 資源不存在
- 500 - 服務器錯誤
