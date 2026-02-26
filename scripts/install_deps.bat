@echo off
chcp 65001 >nul
echo ========================================
echo mPower_Rag 依赖安装脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv311" (
    echo [错误] 虚拟环境不存在
    echo 请先运行以下命令创建虚拟环境:
    echo   python -m venv venv311
    echo   .\venv311\Scripts\Activate
    pause
    exit /b 1
)

echo [1/4] 激活虚拟环境...
call venv311\Scripts\Activate.bat

echo.
echo [2/4] 升级 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [3/4] 安装依赖...
echo 使用清华镜像安装...
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [警告] 部分包可能安装失败，尝试使用阿里云镜像...
    pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
)

echo.
echo [4/4] 验证安装...
python -c "import fastapi; import streamlit; import qdrant_client; print('核心包安装成功!')"

if %errorlevel% neq 0 (
    echo.
    echo [错误] 部分包验证失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步:
echo   1. 启动 Qdrant: docker-compose up -d qdrant
echo   2. 启动 API: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
echo   3. 启动前端: streamlit run frontend/app.py --server.port 8501
echo.
pause
