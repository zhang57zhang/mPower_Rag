@echo off
REM mPower_Rag 开发恢复脚本 (Windows 版本)

echo.
echo ============================================================
echo   mPower_Rag 开发恢复
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 运行恢复脚本
python scripts\resume.py

echo.
echo ============================================================
echo   按任意键关闭...
echo ============================================================
pause >nul
