#!/bin/bash
# mPower_Rag 生产环境部署脚本
# 创建时间: 2026-03-10

set -e  # 遇到错误立即退出

# ==================== 配置 ====================

PROJECT_NAME="mPower_Rag"
VERSION="1.0.0"
COMPOSE_FILE="docker-compose.prod.yml"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==================== 函数定义 ====================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装"
        exit 1
    fi
}

check_env_file() {
    if [ ! -f .env ]; then
        log_error ".env 文件不存在"
        log_info "请复制 .env.production 为 .env 并配置"
        exit 1
    fi
}

# ==================== 检查依赖 ====================

log_info "检查依赖..."

check_command docker
check_command docker-compose

# ==================== 检查配置 ====================

log_info "检查配置..."

check_env_file

# 检查必要的配置项
if grep -q "your_deepseek_api_key_here" .env; then
    log_error "请配置 LLM_API_KEY"
    exit 1
fi

if grep -q "your_production_api_key" .env; then
    log_error "请配置 API_KEYS"
    exit 1
fi

if grep -q "https://your-domain.com" .env; then
    log_warn "CORS_ORIGINS 配置为示例域名，建议修改为实际域名"
fi

# ==================== 停止旧服务 ====================

log_info "停止旧服务..."

docker-compose -f $COMPOSE_FILE down || true

# ==================== 清理旧镜像 ====================

log_info "清理旧镜像..."

docker image prune -f

# ==================== 构建镜像 ====================

log_info "构建 Docker 镜像..."

docker-compose -f $COMPOSE_FILE build --no-cache

# ==================== 启动服务 ====================

log_info "启动服务..."

docker-compose -f $COMPOSE_FILE up -d

# ==================== 等待服务就绪 ====================

log_info "等待服务就绪..."

# 等待 Qdrant
log_info "等待 Qdrant..."
for i in {1..30}; do
    if curl -f http://localhost:6333/health &> /dev/null; then
        log_info "Qdrant 已就绪"
        break
    fi
    sleep 2
done

# 等待 Redis
log_info "等待 Redis..."
for i in {1..30}; do
    if docker exec mpower-rag-redis redis-cli ping &> /dev/null; then
        log_info "Redis 已就绪"
        break
    fi
    sleep 2
done

# 等待 API
log_info "等待 API..."
for i in {1..60}; do
    if curl -f http://localhost:8000/health/live &> /dev/null; then
        log_info "API 已就绪"
        break
    fi
    sleep 3
done

# ==================== 健康检查 ====================

log_info "执行健康检查..."

# 完整健康检查
HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')

if [ "$HEALTH_STATUS" == "healthy" ]; then
    log_info "✅ 所有服务健康"
elif [ "$HEALTH_STATUS" == "degraded" ]; then
    log_warn "⚠️ 服务状态降级，请检查日志"
else
    log_error "❌ 服务不健康，请检查日志"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

# ==================== 显示服务信息 ====================

log_info "服务信息："
echo ""
echo "  📍 API 地址: http://localhost:8000"
echo "  📚 API 文档: http://localhost:8000/docs"
echo "  ❤️  健康检查: http://localhost:8000/health"
echo "  📊 Prometheus: http://localhost:9090"
echo "  📈 Grafana: http://localhost:3000 (admin/${GRAFANA_PASSWORD:-admin})"
echo ""
echo "  🐳 查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "  🛑 停止服务: docker-compose -f $COMPOSE_FILE down"
echo ""

# ==================== 创建备份目录 ====================

log_info "创建备份目录..."

mkdir -p backups/{qdrant,redis,logs}

# ==================== 完成 ====================

log_info "✅ $PROJECT_NAME v$VERSION 部署完成！"
