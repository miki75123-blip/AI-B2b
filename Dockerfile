# AI LeadGen Agent - Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE ${PORT:-8000}

# 使用 Railway 注入的 PORT 环境变量
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
