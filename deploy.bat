@echo off
REM Windows部署脚本 - Docker Compose

setlocal enabledelayedexpansion

echo ==========================================
echo mPower_Rag - 部署脚本
echo ==========================================

REM 检查Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未安装
    echo 请先安装Docker Desktop: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

REM 检查.env文件
if not exist .env (
    echo 警告: .env文件不存在
    echo 从.env.example创建.env文件...
    copy .env.example .env
    echo .env文件已创建
    echo 请编辑.env文件，填入实际的配置值
    echo 特别是LLM_API_KEY
    pause
)

REM 检查必需的环境变量
findstr /C:"LLM_API_KEY=your_" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo 错误: 请在.env文件中设置LLM_API_KEY
    exit /b 1
)

echo.
echo 请选择部署模式:
echo 1) 标准部署 (API + Qdrant)
echo 2) 完整部署 (API + Qdrant + Frontend + 监控)
echo 3) 仅Qdrant
echo 4) 仅API
echo 5) 停止服务
echo 6) 查看状态
echo 7) 查看日志
echo 8) 重新构建
set /p choice="请输入选项 (1-8): "

if "%choice%"=="1" (
    echo 部署: API + Qdrant
    docker-compose up -d qdrant api
) else if "%choice%"=="2" (
    echo 部署: 完整服务
    docker-compose up -d
) else if "%choice%"=="3" (
    echo 部署: 仅Qdrant
    docker-compose up -d qdrant
) else if "%choice%"=="4" (
    echo 部署: 仅API
    docker-compose up -d api
) else if "%choice%"=="5" (
    echo 停止服务
    docker-compose down
    echo 服务已停止
) else if "%choice%"=="6" (
    echo 服务状态:
    docker-compose ps
) else if "%choice%"=="7" (
    echo 服务日志:
    docker-compose logs -f
) else if "%choice%"=="8" (
    echo 重新构建镜像
    docker-compose build --no-cache
    echo 镜像重建完成
    set /p start="是否启动服务? (y/n): "
    if "!start!"=="y" (
        docker-compose up -d
    )
) else (
    echo 无效选项
    exit /b 1
)

REM 显示服务信息
if "%choice%" leq "4" (
    echo.
    echo ==========================================
    echo 服务已部署
    echo ==========================================
    echo.
    echo 访问地址:
    echo   - API文档: http://localhost:8000/docs
    echo   - API健康: http://localhost:8000/health
    echo   - Qdrant:  http://localhost:6333
    if "%choice%"=="2" (
        echo   - 前端界面: http://localhost:8501
        echo   - Prometheus: http://localhost:9090
        echo   - Grafana:   http://localhost:3000
    )
    echo.
    echo 查看日志: docker-compose logs -f
    echo 停止服务: docker-compose down
    echo ==========================================
)

endlocal
