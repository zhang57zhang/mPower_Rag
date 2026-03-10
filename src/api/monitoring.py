"""
监控指标模块
提供 Prometheus 监控指标
"""
import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, Info
import logging

logger = logging.getLogger(__name__)

# ==================== Prometheus 指标定义 ====================

# HTTP 请求计数
HTTP_REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# HTTP 请求延迟
HTTP_REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# RAG 查询计数
RAG_QUERY_COUNT = Counter(
    'rag_queries_total',
    'Total RAG queries',
    ['status', 'use_rerank']
)

# RAG 查询延迟
RAG_QUERY_LATENCY = Histogram(
    'rag_query_duration_seconds',
    'RAG query latency',
    ['stage'],  # retrieval, rerank, llm, total
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# 向量检索计数
VECTOR_SEARCH_COUNT = Counter(
    'vector_search_total',
    'Total vector searches',
    ['status']
)

# 向量检索延迟
VECTOR_SEARCH_LATENCY = Histogram(
    'vector_search_duration_seconds',
    'Vector search latency',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

# LLM 调用计数
LLM_CALL_COUNT = Counter(
    'llm_calls_total',
    'Total LLM API calls',
    ['provider', 'model', 'status']
)

# LLM 调用延迟
LLM_CALL_LATENCY = Histogram(
    'llm_call_duration_seconds',
    'LLM API call latency',
    ['provider', 'model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# 缓存命中计数
CACHE_HIT_COUNT = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']  # query, retrieval, llm
)

# 缓存未命中计数
CACHE_MISS_COUNT = Counter(
    'cache_miss_total',
    'Total cache misses',
    ['cache_type']
)

# 活跃连接数
ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

# 文档数量
DOCUMENT_COUNT = Gauge(
    'documents_total',
    'Total number of documents in knowledge base'
)

# 应用信息
APP_INFO = Info(
    'app',
    'Application information'
)


# ==================== 中间件 ====================

class MonitoringMiddleware:
    """监控中间件"""
    
    def __init__(self, app):
        self.app = app
        
        # 设置应用信息
        try:
            from config.settings import settings
            APP_INFO.info({
                'name': settings.app_name,
                'version': settings.app_version,
                'debug': str(settings.debug)
            })
        except Exception as e:
            logger.warning(f"Failed to set app info: {e}")
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        中间件调用
        
        Args:
            request: 请求对象
            call_next: 下一个中间件
            
        Returns:
            响应
        """
        # 跳过监控端点
        if request.url.path in ["/metrics", "/health", "/health/live", "/health/ready", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # 记录开始时间
        start_time = time.time()
        
        # 增加活跃连接数
        ACTIVE_CONNECTIONS.inc()
        
        try:
            # 调用下一个中间件
            response = await call_next(request)
            
            # 记录指标
            duration = time.time() - start_time
            
            # 获取端点（去除路径参数）
            endpoint = self._get_endpoint_pattern(request.url.path)
            
            # 记录 HTTP 指标
            HTTP_REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            HTTP_REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # 记录错误
            logger.error(f"Request failed: {e}")
            raise
            
        finally:
            # 减少活跃连接数
            ACTIVE_CONNECTIONS.dec()
    
    def _get_endpoint_pattern(self, path: str) -> str:
        """
        获取端点模式（去除路径参数）
        
        Args:
            path: 请求路径
            
        Returns:
            端点模式
        """
        # 简单处理：将数字替换为 {id}
        import re
        pattern = re.sub(r'/\d+', '/{id}', path)
        return pattern


# ==================== 辅助函数 ====================

def track_rag_query(status: str, use_rerank: bool, duration: float):
    """
    记录 RAG 查询指标
    
    Args:
        status: 查询状态（success, error）
        use_rerank: 是否使用重排序
        duration: 持续时间（秒）
    """
    RAG_QUERY_COUNT.labels(status=status, use_rerank=str(use_rerank)).inc()
    RAG_QUERY_LATENCY.labels(stage='total').observe(duration)


def track_vector_search(status: str, duration: float):
    """
    记录向量检索指标
    
    Args:
        status: 检索状态（success, error）
        duration: 持续时间（秒）
    """
    VECTOR_SEARCH_COUNT.labels(status=status).inc()
    VECTOR_SEARCH_LATENCY.observe(duration)


def track_llm_call(provider: str, model: str, status: str, duration: float):
    """
    记录 LLM 调用指标
    
    Args:
        provider: LLM 提供商
        model: 模型名称
        status: 调用状态（success, error, timeout）
        duration: 持续时间（秒）
    """
    LLM_CALL_COUNT.labels(provider=provider, model=model, status=status).inc()
    LLM_CALL_LATENCY.labels(provider=provider, model=model).observe(duration)


def track_cache_hit(cache_type: str):
    """
    记录缓存命中
    
    Args:
        cache_type: 缓存类型（query, retrieval, llm）
    """
    CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """
    记录缓存未命中
    
    Args:
        cache_type: 缓存类型（query, retrieval, llm）
    """
    CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()


def update_document_count(count: int):
    """
    更新文档数量
    
    Args:
        count: 文档数量
    """
    DOCUMENT_COUNT.set(count)
