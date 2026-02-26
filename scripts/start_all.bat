@echo off
echo ========================================
echo mPower_Rag 服务启动脚本
echo ========================================

echo.
echo 1. 检查 Docker 是否运行...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 未运行，请先启动 Docker
    pause
    exit /b 1
)
echo [OK] Docker 正在运行

echo.
echo 2. 启动 Qdrant 向量数据库...
docker-compose up -d qdrant
if %errorlevel% neq 0 (
    echo [错误] Qdrant 启动失败
    pause
    exit /b 1
)
echo [OK] Qdrant 已启动

echo.
echo 3. 等待 Qdrant 准备就绪...
timeout /t 5 /nobreak >nul

echo.
echo 4. 启动 FastAPI 后端服务...
start "mPower_Rag API" cmd /k "cd /d %~dp0\.. && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

echo.
echo 5. 启动 Streamlit 前端服务...
start "mPower_Rag Frontend" cmd /k "cd /d %~dp0\.. && streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 访问地址：
echo   - 前端: http://localhost:8501
echo   - API:  http://localhost:8000
echo   - API 文档: http://localhost:8000/docs
echo.
echo 提示：请确保 .env 文件已配置 LLM_API_KEY
echo.
pause
