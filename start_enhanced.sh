#!/bin/bash

echo "===================================="
echo "mPower_Rag 增强版 - 启动中..."
echo "===================================="
echo ""

# 进入脚本所在目录
cd "$(dirname "$0")"

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi
python3 --version

echo ""
echo "[2/3] 安装依赖..."
pip3 install fastapi uvicorn python-multipart python-docx openpyxl PyPDF2 -q

echo ""
echo "[3/3] 启动增强版API服务..."
echo ""
echo "===================================="
echo "🌐 API文档: http://localhost:8000/docs"
echo "📚 知识库管理: http://localhost:8000/api/v1/documents"
echo "🔌 外部API: http://localhost:8000/api/v1/external/query"
echo "===================================="
echo ""

python3 api_enhanced.py
