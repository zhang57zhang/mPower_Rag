@echo off
chcp 65001 >nul
echo ====================================
echo mPower_Rag 增强版 - 启动中...
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖...
pip install fastapi uvicorn python-multipart python-docx openpyxl PyPDF2 -q
if errorlevel 1 (
    echo ⚠️ 依赖安装失败，但继续尝试启动
)

echo.
echo [3/3] 启动增强版API服务...
echo.
echo ====================================
echo 🌐 API文档: http://localhost:8000/docs
echo 📚 知识库管理: http://localhost:8000/api/v1/documents
echo 🔌 外部API: http://localhost:8000/api/v1/external/query
echo ====================================
echo.

python api_enhanced.py

pause
