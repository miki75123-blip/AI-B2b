@echo off
chcp 65001 >nul
echo ============================================
echo   AI LeadGen Agent - GitHub 上傳腳本
echo ============================================
echo.

cd /d "%~dp0"

REM 檢查 Git
where git >nul 2>&1
if errorlevel 1 (
    echo [錯誤] Git 未找到
    echo.
    echo 請重新打開終端窗口，然後再次運行此腳本
    echo 或手動運行以下命令：
    echo.
    echo   git init
    echo   git add .
    echo   git commit -m "first commit"
    echo   git branch -M main
    echo   git remote add origin https://github.com/YOUR_USERNAME/ai-leadgen-agent.git
    echo   git push -u origin main
    pause
    exit /b 1
)

echo [1/4] 初始化 Git 倉庫...
git init
git branch -M main

echo.
echo [2/4] 添加文件到 Git...
git add .

echo.
echo [3/4] 提交文件...
git commit -m "AI LeadGen Agent - Initial commit"

echo.
echo [4/4] 準備上傳到 GitHub
echo.
echo ============================================
echo   請在 GitHub 創建倉庫後運行：
echo.
echo   git remote add origin https://github.com/YOUR_USERNAME/ai-leadgen-agent.git
echo   git push -u origin main
echo ============================================
echo.

set /p REPO_URL="請粘貼 GitHub 倉庫 URL: "

if not "%REPO_URL%"=="" (
    echo.
    echo 連接到 GitHub 並上傳...
    git remote add origin %REPO_URL%
    git push -u origin main
    echo.
    echo 上傳完成！
) else (
    echo 已跳過上傳，請手動執行 git push
)

pause
