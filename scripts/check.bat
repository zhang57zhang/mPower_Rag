@echo off
REM mPower_Rag 环境检查脚本 (Windows 版本)

echo.
echo ============================================================
echo   mPower_Rag 环境检查
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 运行检查脚本
python scripts\check.py

REM 检查结果
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   检查失败，请解决上述问题
    echo ============================================================
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================
    echo   环境检查通过！
    echo ============================================================
)
