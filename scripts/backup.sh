#!/bin/bash
# mPower_Rag 备份脚本
# 创建时间: 2026-03-10

set -e

# ==================== 配置 ====================

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

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

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# ==================== 创建备份目录 ====================

log_info "创建备份目录..."

mkdir -p "$BACKUP_DIR"/{qdrant,redis,logs}

# ==================== 备份 Qdrant ====================

log_info "备份 Qdrant 数据..."

QDRANT_BACKUP_FILE="$BACKUP_DIR/qdrant/backup_$TIMESTAMP.tar.gz"

# 使用 Qdrant 快照 API
curl -X POST "http://localhost:6333/collections/vehicle_test_knowledge/snapshots" \
    -H "Content-Type: application/json" \
    -d '{"action": "create_snapshot"}'

# 等待快照完成
sleep 5

# 从容器复制快照文件
docker cp mpower-rag-qdrant:/qdrant/storage /tmp/qdrant_backup_$TIMESTAMP

# 压缩备份
tar -czf "$QDRANT_BACKUP_FILE" -C /tmp qdrant_backup_$TIMESTAMP

# 清理临时文件
rm -rf /tmp/qdrant_backup_$TIMESTAMP

log_success "Qdrant 备份完成: $QDRANT_BACKUP_FILE"

# ==================== 备份 Redis ====================

log_info "备份 Redis 数据..."

REDIS_BACKUP_FILE="$BACKUP_DIR/redis/backup_$TIMESTAMP.rdb"

# 触发 Redis RDB 快照
docker exec mpower-rag-redis redis-cli BGSAVE

# 等待快照完成
sleep 3

# 复制 RDB 文件
docker cp mpower-rag-redis:/data/dump.rdb "$REDIS_BACKUP_FILE"

log_success "Redis 备份完成: $REDIS_BACKUP_FILE"

# ==================== 备份日志 ====================

log_info "备份日志文件..."

LOGS_BACKUP_FILE="$BACKUP_DIR/logs/logs_$TIMESTAMP.tar.gz"

if [ -d "logs" ]; then
    tar -czf "$LOGS_BACKUP_FILE" logs/
    log_success "日志备份完成: $LOGS_BACKUP_FILE"
else
    log_info "无日志文件需要备份"
fi

# ==================== 备份配置 ====================

log_info "备份配置文件..."

CONFIG_BACKUP_FILE="$BACKUP_DIR/config_backup_$TIMESTAMP.tar.gz"

tar -czf "$CONFIG_BACKUP_FILE" \
    .env \
    docker-compose.prod.yml \
    config/ 2>/dev/null || true

log_success "配置备份完成: $CONFIG_BACKUP_FILE"

# ==================== 清理旧备份 ====================

log_info "清理旧备份文件（保留 $RETENTION_DAYS 天）..."

find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type f -name "*.rdb" -mtime +$RETENTION_DAYS -delete

log_success "旧备份清理完成"

# ==================== 生成备份报告 ====================

log_info "生成备份报告..."

BACKUP_REPORT="$BACKUP_DIR/backup_report_$TIMESTAMP.txt"

cat > "$BACKUP_REPORT" << EOF
========================================
mPower_Rag 备份报告
========================================

备份时间: $(date '+%Y-%m-%d %H:%M:%S')
备份类型: 完整备份

备份文件:
- Qdrant: $QDRANT_BACKUP_FILE
  大小: $(du -h "$QDRANT_BACKUP_FILE" | cut -f1)
  
- Redis: $REDIS_BACKUP_FILE
  大小: $(du -h "$REDIS_BACKUP_FILE" | cut -f1)
  
- 日志: $LOGS_BACKUP_FILE
  大小: $(du -h "$LOGS_BACKUP_FILE" 2>/dev/null | cut -f1 || echo "无")
  
- 配置: $CONFIG_BACKUP_FILE
  大小: $(du -h "$CONFIG_BACKUP_FILE" | cut -f1)

备份状态: ✅ 成功

备份保留策略: $RETENTION_DAYS 天

========================================
EOF

log_success "备份报告已生成: $BACKUP_REPORT"

# ==================== 完成总结 ====================

echo ""
echo "======================================"
echo "  备份完成"
echo "======================================"
echo ""
log_success "所有备份任务已完成"
echo ""
echo "📦 备份文件位置:"
echo "  - Qdrant: $QDRANT_BACKUP_FILE"
echo "  - Redis: $REDIS_BACKUP_FILE"
echo "  - 日志: $LOGS_BACKUP_FILE"
echo "  - 配置: $CONFIG_BACKUP_FILE"
echo ""
echo "📋 备份报告: $BACKUP_REPORT"
echo ""
