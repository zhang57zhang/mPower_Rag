@echo off
REM Windows 环境启动脚本

echo ====================================
echo mPower_Rag 项目启动脚本
echo ====================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 创建虚拟环境
if not exist "venv" (
    echo [INFO] 创建 Python 虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [INFO] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [INFO] 安装 Python 依赖...
pip install -r requirements.txt

REM 检查环境变量文件
if not exist ".env" (
    echo [INFO] 创建环境变量文件...
    copy .env.example .env
    echo [WARNING] 请编辑 .env 文件，填入你的 API Key
)

REM 创建必要的目录
if not exist "knowledge_base\documents" mkdir knowledge_base\documents
if not exist "knowledge_base\parsed" mkdir knowledge_base\parsed
if not exist "logs" mkdir logs
if not exist "data\chroma" mkdir data\chroma

echo.
echo ====================================
echo [SUCCESS] 项目初始化完成！
echo ====================================
echo.
echo 接下来：
echo 1. 编辑 .env 文件，配置 API Key
echo 2. 运行 'docker-compose up' 启动所有服务（需要 Docker）
echo    或者分别启动服务：
echo    - 后端 API: python src/api/main.py
echo    - 前端: streamlit run frontend/app.py
echo.
pause
