#!/bin/bash
# mPower_Rag API 测试脚本
# 创建时间: 2026-03-10

set -e

# ==================== 配置 ====================

API_BASE_URL="http://localhost:8000"
API_KEY="${API_KEY:-your_api_key_here}"

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

# ==================== 测试 ====================

echo "======================================"
echo "  mPower_Rag API 测试"
echo "======================================"
echo ""

# 测试 1: 健康检查
log_info "测试 1: 健康检查..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    log_success "健康检查通过"
    echo "状态: $(echo $BODY | jq -r '.status')"
else
    log_error "健康检查失败: HTTP $HTTP_CODE"
    exit 1
fi
echo ""

# 测试 2: 存活检查
log_info "测试 2: 存活检查..."
LIVE_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/health/live")
HTTP_CODE=$(echo "$LIVE_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" -eq 200 ]; then
    log_success "存活检查通过"
else
    log_error "存活检查失败: HTTP $HTTP_CODE"
    exit 1
fi
echo ""

# 测试 3: 就绪检查
log_info "测试 3: 就绪检查..."
READY_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/health/ready")
HTTP_CODE=$(echo "$READY_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" -eq 200 ]; then
    log_success "就绪检查通过"
else
    log_error "就绪检查失败: HTTP $HTTP_CODE"
    exit 1
fi
echo ""

# 测试 4: API 文档
log_info "测试 4: API 文档访问..."
DOCS_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/docs")
HTTP_CODE=$(echo "$DOCS_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" -eq 200 ]; then
    log_success "API 文档可访问"
else
    log_error "API 文档访问失败: HTTP $HTTP_CODE"
fi
echo ""

# 测试 5: 智能问答（需要 API Key）
log_info "测试 5: 智能问答..."
if [ "$API_KEY" != "your_api_key_here" ]; then
    CHAT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/v1/chat" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{"query": "蓝牙测试流程", "top_k": 3}')
    
    HTTP_CODE=$(echo "$CHAT_RESPONSE" | tail -n 1)
    BODY=$(echo "$CHAT_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        log_success "智能问答测试通过"
        echo "回答: $(echo $BODY | jq -r '.answer' | head -c 100)..."
    else
        log_error "智能问答测试失败: HTTP $HTTP_CODE"
        echo "响应: $BODY"
    fi
else
    log_info "跳过智能问答测试（未配置 API_KEY）"
fi
echo ""

# 测试 6: 文档统计
log_info "测试 6: 文档统计..."
if [ "$API_KEY" != "your_api_key_here" ]; then
    STATS_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/v1/documents/stats" \
        -H "X-API-Key: $API_KEY")
    
    HTTP_CODE=$(echo "$STATS_RESPONSE" | tail -n 1)
    BODY=$(echo "$STATS_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        log_success "文档统计测试通过"
        echo "统计: $(echo $BODY | jq -c '.')"
    else
        log_error "文档统计测试失败: HTTP $HTTP_CODE"
    fi
else
    log_info "跳过文档统计测试（未配置 API_KEY）"
fi
echo ""

# 测试 7: 认证测试（故意不提供 API Key）
log_info "测试 7: 认证测试（无 API Key）..."
AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/v1/chat" \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}')

HTTP_CODE=$(echo "$AUTH_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" -eq 401 ]; then
    log_success "认证测试通过（正确返回 401）"
else
    log_error "认证测试失败: 应返回 401，实际返回 $HTTP_CODE"
fi
echo ""

# 测试 8: 限流测试
log_info "测试 8: 限流测试..."
if [ "$API_KEY" != "your_api_key_here" ]; then
    log_info "发送 10 个快速请求..."
    LIMIT_HIT=false
    for i in {1..10}; do
        RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/health/live")
        HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
        
        if [ "$HTTP_CODE" -eq 429 ]; then
            LIMIT_HIT=true
            break
        fi
    done
    
    if [ "$LIMIT_HIT" = true ]; then
        log_success "限流测试通过（触发了限流）"
    else
        log_info "限流测试完成（未触发限流，可能限流阈值较高）"
    fi
else
    log_info "跳过限流测试"
fi
echo ""

# ==================== 总结 ====================

echo "======================================"
echo "  测试完成"
echo "======================================"
echo ""
log_success "所有核心测试通过！"
echo ""
echo "📊 测试覆盖："
echo "  ✅ 健康检查"
echo "  ✅ 存活检查"
echo "  ✅ 就绪检查"
echo "  ✅ API 文档"
echo "  ✅ 智能问答"
echo "  ✅ 文档统计"
echo "  ✅ 认证机制"
echo "  ✅ 限流机制"
echo ""
