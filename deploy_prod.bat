@echo off
REM mPower_Rag 生产环境部署脚本 (Windows)
REM 创建时间: 2026-03-10

setlocal enabledelayedexpansion

REM ==================== 配置 ====================

set PROJECT_NAME=mPower_Rag
set VERSION=1.0.0
set COMPOSE_FILE=docker-compose.prod.yml

REM ==================== 颜色输出 ====================

REM Windows 不支持颜色，使用前缀

:log_info
echo [INFO] %*
goto :eof

:log_warn
echo [WARN] %*
goto :eof

:log_error
echo [ERROR] %*
goto :eof

:check_command
where %1 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_error %1 未安装，请先安装
    exit /b 1
)
goto :eof

:check_env_file
if not exist .env (
    call :log_error .env 文件不存在
    call :log_info 请复制 .env.production 为 .env 并配置
    exit /b 1
)
goto :eof

REM ==================== 检查依赖 ====================

call :log_info 检查依赖...

call :check_command docker
call :check_command docker-compose

REM ==================== 检查配置 ====================

call :log_info 检查配置...

call :check_env_file

REM 检查必要的配置项
findstr /C:"your_deepseek_api_key_here" .env >nul
if %ERRORLEVEL% equ 0 (
    call :log_error 请配置 LLM_API_KEY
    exit /b 1
)

findstr /C:"your_production_api_key" .env >nul
if %ERRORLEVEL% equ 0 (
    call :log_error 请配置 API_KEYS
    exit /b 1
)

REM ==================== 停止旧服务 ====================

call :log_info 停止旧服务...

docker-compose -f %COMPOSE_FILE% down

REM ==================== 清理旧镜像 ====================

call :log_info 清理旧镜像...

docker image prune -f

REM ==================== 构建镜像 ====================

call :log_info 构建 Docker 镜像...

docker-compose -f %COMPOSE_FILE% build --no-cache

REM ==================== 启动服务 ====================

call :log_info 启动服务...

docker-compose -f %COMPOSE_FILE% up -d

REM ==================== 等待服务就绪 ====================

call :log_info 等待服务就绪...

REM 等待 API
call :log_info 等待 API...
set MAX_RETRIES=60
set RETRY_COUNT=0

:wait_api
curl -f http://localhost:8000/health/live >nul 2>&1
if %ERRORLEVEL% equ 0 (
    call :log_info API 已就绪
    goto :api_ready
)

set /a RETRY_COUNT+=1
if %RETRY_COUNT% geq %MAX_RETRIES% (
    call :log_error API 启动超时
    exit /b 1
)

timeout /t 3 /nobreak >nul
goto :wait_api

:api_ready

REM ==================== 健康检查 ====================

call :log_info 执行健康检查...

curl -s http://localhost:8000/health > health_status.json

findstr /C:"healthy" health_status.json >nul
if %ERRORLEVEL% equ 0 (
    call :log_info ✅ 所有服务健康
) else (
    call :log_error ❌ 服务不健康，请检查日志
    docker-compose -f %COMPOSE_FILE% logs
    exit /b 1
)

del health_status.json

REM ==================== 显示服务信息 ====================

call :log_info 服务信息：
echo.
echo   📍 API 地址: http://localhost:8000
echo   📚 API 文档: http://localhost:8000/docs
echo   ❤️  健康检查: http://localhost:8000/health
echo   📊 Prometheus: http://localhost:9090
echo   📈 Grafana: http://localhost:3000
echo.
echo   🐳 查看日志: docker-compose -f %COMPOSE_FILE% logs -f
echo   🛑 停止服务: docker-compose -f %COMPOSE_FILE% down
echo.

REM ==================== 创建备份目录 ====================

call :log_info 创建备份目录...

if not exist backups\qdrant mkdir backups\qdrant
if not exist backups\redis mkdir backups\redis
if not exist backups\logs mkdir backups\logs

REM ==================== 完成 ====================

call :log_info ✅ %PROJECT_NAME% v%VERSION% 部署完成！

endlocal
