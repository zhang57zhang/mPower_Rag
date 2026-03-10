#!/bin/bash
# mPower_Rag 恢复脚本
# 创建时间: 2026-03-10

set -e

# ==================== 配置 ====================

BACKUP_DIR="backups"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ==================== 函数 ====================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# ==================== 检查参数 ====================

if [ $# -lt 2 ]; then
    log_error "用法: $0 <type> <backup_file>"
    echo ""
    echo "类型:"
    echo "  qdrant    - 恢复 Qdrant 数据"
    echo "  redis     - 恢复 Redis 数据"
    echo ""
    echo "示例:"
    echo "  $0 qdrant backups/qdrant/backup_20260310_020000.tar.gz"
    echo "  $0 redis backups/redis/backup_20260310_020000.rdb"
    exit 1
fi

TYPE=$1
BACKUP_FILE=$2

# ==================== 验证备份文件 ====================

if [ ! -f "$BACKUP_FILE" ]; then
    log_error "备份文件不存在: $BACKUP_FILE"
    exit 1
fi

log_info "准备恢复 $TYPE 数据..."
log_info "备份文件: $BACKUP_FILE"

# ==================== 确认恢复 ====================

log_warn "⚠️  恢复操作将覆盖当前数据！"
read -p "确认继续? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "恢复操作已取消"
    exit 0
fi

# ==================== 执行恢复 ====================

case $TYPE in
    qdrant)
        log_info "恢复 Qdrant 数据..."
        
        # 停止 API 服务
        log_info "停止 API 服务..."
        docker-compose -f docker-compose.prod.yml stop api
        
        # 解压备份文件
        log_info "解压备份文件..."
        tar -xzf "$BACKUP_FILE" -C /tmp
        
        # 获取解压后的目录名
        BACKUP_DIR_NAME=$(tar -tzf "$BACKUP_FILE" | head -1 | cut -f1 -d"/")
        
        # 恢复数据
        log_info "恢复数据到 Qdrant 容器..."
        docker cp "/tmp/$BACKUP_DIR_NAME" mpower-rag-qdrant:/qdrant/storage_restored
        
        # 重启 Qdrant（使用恢复的数据）
        log_info "重启 Qdrant 服务..."
        docker-compose -f docker-compose.prod.yml restart qdrant
        
        # 等待 Qdrant 启动
        sleep 10
        
        # 启动 API 服务
        log_info "启动 API 服务..."
        docker-compose -f docker-compose.prod.yml start api
        
        # 清理临时文件
        rm -rf "/tmp/$BACKUP_DIR_NAME"
        
        log_success "Qdrant 数据恢复完成"
        ;;
        
    redis)
        log_info "恢复 Redis 数据..."
        
        # 停止 Redis 服务
        log_info "停止 Redis 服务..."
        docker-compose -f docker-compose.prod.yml stop redis
        
        # 复制备份文件
        log_info "恢复数据文件..."
        docker cp "$BACKUP_FILE" mpower-rag-redis:/data/dump.rdb
        
        # 启动 Redis 服务
        log_info "启动 Redis 服务..."
        docker-compose -f docker-compose.prod.yml start redis
        
        # 等待 Redis 启动
        sleep 5
        
        # 验证数据
        log_info "验证数据恢复..."
        docker exec mpower-rag-redis redis-cli DBSIZE
        
        log_success "Redis 数据恢复完成"
        ;;
        
    *)
        log_error "未知类型: $TYPE"
        exit 1
        ;;
esac

# ==================== 验证恢复 ====================

log_info "验证服务状态..."

# 等待服务完全启动
sleep 5

# 健康检查
HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')

if [ "$HEALTH_STATUS" == "healthy" ]; then
    log_success "✅ 服务状态正常"
else
    log_error "❌ 服务状态异常: $HEALTH_STATUS"
    log_error "请检查日志: docker-compose -f docker-compose.prod.yml logs"
fi

# ==================== 完成 ====================

echo ""
echo "======================================"
echo "  恢复完成"
echo "======================================"
echo ""
log_success "$TYPE 数据已成功恢复"
echo ""
