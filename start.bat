@echo off
chcp 65001 >nul
echo ============================================
echo   AI LeadGen Agent - 快速啟動腳本
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] 檢查 Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 未找到 Docker，請先安裝 Docker Desktop
    pause
    exit /b 1
)
echo     ✓ Docker 已就緒

echo.
echo [2/4] 檢查 .env 配置文件...
if not exist ".env" (
    echo     創建 .env 文件...
    copy .env.example .env
    echo.
    echo     ⚠️  請編輯 .env 文件填入您的 API Keys:
    echo        - OPENAI_API_KEY
    echo        - SENDGRID_API_KEY
    echo.
    notepad .env
)

echo.
echo [3/4] 啟動 Docker 服務...
docker-compose up -d

echo.
echo [4/4] 等待服務啟動...
timeout /t 10 /nobreak >nul

echo.
echo ============================================
echo   服務已啟動！
echo ============================================
echo.
echo   前端網站:  http://localhost:5173
echo   API 文檔:  http://localhost:8000/docs
echo   任務監控:  http://localhost:5555
echo.
echo   查看日誌: docker-compose logs -f
echo   停止服務: docker-compose down
echo ============================================
echo.
echo   按任意鍵打開瀏覽器...
pause >nul
start http://localhost:5173
