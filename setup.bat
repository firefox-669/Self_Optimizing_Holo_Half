@echo off
REM Self_Optimizing_Holo_Half - Windows 一键安装脚本
REM 实现真正的 "git clone 即用"

echo ============================================================
echo Self_Optimizing_Holo_Half - Quick Setup
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

REM 检查 pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)
echo [OK] pip found
echo.

REM 安装依赖
echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM 初始化数据库
echo [2/4] Initializing database...
python user_scoring/database.py
if errorlevel 1 (
    echo [ERROR] Failed to initialize database
    pause
    exit /b 1
)
echo [OK] Database initialized
echo.

REM 创建 .env 文件
echo [3/4] Setting up environment...
if not exist .env (
    copy .env.example .env >nul
    echo [OK] Created .env file from template
    echo.
    echo [IMPORTANT] Please edit .env and add your API keys:
    echo   - LLM_API_KEY (required)
    echo   - OPENHANDS_API_URL (if using OpenHands)
    echo   - OPENSPACE_API_URL (if using OpenSpace)
    echo.
) else (
    echo [OK] .env file already exists
)
echo.

REM 运行测试
echo [4/4] Running tests...
python test_ab_testing.py
if errorlevel 1 (
    echo [WARNING] Some tests failed, but installation completed
) else (
    echo [OK] All tests passed!
)
echo.

echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Edit .env file with your API keys
echo   2. Start OpenHands service (if using): http://localhost:3000
echo   3. Run: python main.py --mode normal
echo.
echo For more help, see INSTALLATION_GUIDE.md
echo.
pause
