# AI LeadGen Agent - Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴 (Playwright 需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright 瀏覽器
RUN playwright install chromium && playwright install-deps chromium

COPY backend/ .

EXPOSE 8000

# 使用固定端口，Railway 會自動映射
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
