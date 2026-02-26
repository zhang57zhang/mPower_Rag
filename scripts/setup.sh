#!/bin/bash

echo "===================================="
echo "mPower_Rag 项目启动脚本"
echo "===================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 未安装"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 未安装"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[INFO] 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[INFO] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[INFO] 安装 Python 依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "[INFO] 创建环境变量文件..."
    cp .env.example .env
    echo "[WARNING] 请编辑 .env 文件，填入你的 API Key"
fi

# 创建必要的目录
mkdir -p knowledge_base/documents
mkdir -p knowledge_base/parsed
mkdir -p logs
mkdir -p data/chroma

echo ""
echo "===================================="
echo "[SUCCESS] 项目初始化完成！"
echo "===================================="
echo ""
echo "接下来："
echo "1. 编辑 .env 文件，配置 API Key"
echo "2. 运行 'docker-compose up' 启动所有服务（需要 Docker）"
echo "   或者分别启动服务："
echo "   - 后端 API: python src/api/main.py"
echo "   - 前端: streamlit run frontend/app.py"
echo ""
