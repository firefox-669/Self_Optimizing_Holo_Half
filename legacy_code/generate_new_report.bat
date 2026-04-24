@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 生成新的进化报告
echo ========================================
echo.
python generate_report.py
echo.
echo ========================================
echo 完成！请查看 reports 目录
echo ========================================
pause
