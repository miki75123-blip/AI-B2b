# 使用官方 Python 運行時
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 複製依賴文件
COPY backend/requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY backend/ .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
