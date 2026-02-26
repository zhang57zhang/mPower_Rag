#!/bin/bash
# 部署脚本 - Docker Compose

set -e

echo "=========================================="
echo "mPower_Rag - 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env文件不存在${NC}"
    echo "从.env.example创建.env文件..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env文件已创建${NC}"
    echo -e "${YELLOW}请编辑.env文件，填入实际的配置值${NC}"
    echo -e "${YELLOW}特别是LLM_API_KEY${NC}"
    read -p "按Enter继续..."
fi

# 检查必需的环境变量
if ! grep -q "^LLM_API_KEY=" .env || grep -q "^LLM_API_KEY=your_" .env; then
    echo -e "${RED}错误: 请在.env文件中设置LLM_API_KEY${NC}"
    exit 1
fi

# 显示部署选项
echo ""
echo "请选择部署模式:"
echo "1) 标准部署 (API + Qdrant)"
echo "2) 完整部署 (API + Qdrant + Frontend + 监控)"
echo "3) 仅Qdrant"
echo "4) 仅API"
echo "5) 停止服务"
echo "6) 查看状态"
echo "7) 查看日志"
echo "8) 重新构建"
read -p "请输入选项 (1-8): " choice

case $choice in
    1)
        echo -e "${GREEN}部署: API + Qdrant${NC}"
        docker-compose up -d qdrant api
        ;;
    2)
        echo -e "${GREEN}部署: 完整服务${NC}"
        docker-compose up -d
        ;;
    3)
        echo -e "${GREEN}部署: 仅Qdrant${NC}"
        docker-compose up -d qdrant
        ;;
    4)
        echo -e "${GREEN}部署: 仅API${NC}"
        docker-compose up -d api
        ;;
    5)
        echo -e "${YELLOW}停止服务${NC}"
        docker-compose down
        echo -e "${GREEN}✓ 服务已停止${NC}"
        ;;
    6)
        echo "服务状态:"
        docker-compose ps
        ;;
    7)
        echo "服务日志:"
        docker-compose logs -f
        ;;
    8)
        echo -e "${YELLOW}重新构建镜像${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}✓ 镜像重建完成${NC}"
        read -p "是否启动服务? (y/n): " start
        if [ "$start" = "y" ]; then
            docker-compose up -d
        fi
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

# 显示服务信息
if [[ $choice =~ ^[1-4]$ ]]; then
    echo ""
    echo "=========================================="
    echo "服务已部署"
    echo "=========================================="
    echo ""
    echo "访问地址:"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - API健康: http://localhost:8000/health"
    echo "  - Qdrant:  http://localhost:6333"
    if [ "$choice" = "2" ]; then
        echo "  - 前端界面: http://localhost:8501"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana:   http://localhost:3000"
    fi
    echo ""
    echo "查看日志: docker-compose logs -f"
    echo "停止服务: docker-compose down"
    echo "=========================================="
fi
