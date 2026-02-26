@echo off
chcp 65001 >nul
echo ========================================
echo mPower_Rag 服务启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv311" (
    echo [错误] 虚拟环境不存在
    echo 请先运行: install_deps.bat
    pause
    exit /b 1
)

echo [1/3] 启动 Qdrant...
docker-compose up -d qdrant
if %errorlevel% neq 0 (
    echo [警告] Qdrant 启动失败，请检查 Docker
)
echo.

echo [2/3] 启动 FastAPI...
start "mPower_Rag API" cmd /k "call venv311\Scripts\Activate.bat && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"
echo.

timeout /t 3 /nobreak >nul

echo [3/3] 启动 Streamlit...
start "mPower_Rag Frontend" cmd /k "call venv311\Scripts\Activate.bat && streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"
echo.

echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 访问地址:
echo   - 前端: http://localhost:8501
echo   - API:  http://localhost:8000
echo   - API 文档: http://localhost:8000/docs
echo.
echo 注意:
echo   - 首次启动可能需要下载模型（sentence-transformers）
echo   - 如果遇到错误，请查看终端输出
echo.
pause
