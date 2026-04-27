@echo off
chcp 65001 >nul
echo ============================================
echo   AI LeadGen Agent - 本地啟動腳本
echo   (無需 Docker)
echo ============================================
echo.

cd /d "%~dp0"

REM 複製環境配置
if not exist ".env" (
    echo [1/5] 複製環境配置...
    copy .env.local .env
    echo     ✓ 已創建 .env
    echo.
    echo     ⚠️  請編輯 .env 填入 OPENAI_API_KEY
    echo.
)

echo [2/5] 安裝後端依賴...
cd backend
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo     ⚠️  pip 安裝有警告，但繼續...
)

echo.
echo [3/5] 安裝前端依賴...
cd ..\frontend
call npm install

echo.
echo [4/5] 初始化數據庫...
cd ..\backend
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine); print('    ✓ 數據庫已就緒')"

echo.
echo [5/5] 啟動服務...
echo.
echo ============================================
echo   正在啟動後端和前端...
echo   請在新窗口中查看日誌
echo ============================================
echo.

REM 啟動後端
start "AI LeadGen - Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"

REM 等待後端啟動
timeout /t 3 /nobreak >nul

REM 啟動前端
start "AI LeadGen - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo   服務已啟動！
echo ============================================
echo.
echo   前端網站:  http://localhost:5173
echo   API 文檔:  http://localhost:8000/docs
echo.
echo   按任意鍵打開瀏覽器...
pause >nul
start http://localhost:5173
