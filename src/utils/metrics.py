"""
Prometheus 监控指标
RAG 系统核心指标暴露
"""
import logging
import time
from typing import Callable
from functools import wraps
from fastapi import Request, Response

logger = logging.getLogger(__name__)

# 延迟导入 prometheus_client
_metrics_enabled = False

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Info,
        generate_latest, CONTENT_TYPE_LATEST,
        REGISTRY
    )
    _metrics_enabled = True
    logger.info("Prometheus 指标已启用")
except ImportError:
    logger.warning("prometheus_client 未安装，监控指标不可用")
    Counter = Histogram = Gauge = Info = None


# ========== 指标定义 ==========

if _metrics_enabled:
    # 请求计数器
    REQUEST_COUNT = Counter(
        'rag_http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )

    # 请求延迟
    REQUEST_LATENCY = Histogram(
        'rag_http_request_duration_seconds',
        'HTTP request latency',
        ['method', 'endpoint'],
        buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    )

    # 检索延迟
    RETRIEVAL_LATENCY = Histogram(
        'rag_retrieval_latency_seconds',
        'Vector retrieval latency',
        ['method'],
        buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
    )

    # 检索召回数量
    RETRIEVAL_DOCS = Histogram(
        'rag_retrieval_docs_count',
        'Number of documents retrieved',
        ['method'],
        buckets=[1, 3, 5, 10, 20, 50]
    )

    # LLM 生成延迟
    LLM_LATENCY = Histogram(
        'rag_llm_generation_latency_seconds',
        'LLM generation latency',
        ['model'],
        buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
    )

    # LLM Token 使用量
    LLM_TOKENS = Counter(
        'rag_llm_tokens_total',
        'Total LLM tokens used',
        ['model', 'type']  # type: input/output
    )

    # 缓存命中率
    CACHE_HITS = Counter(
        'rag_cache_hits_total',
        'Total cache hits',
        ['cache_type']  # query/retrieval/llm
    )

    CACHE_MISSES = Counter(
        'rag_cache_misses_total',
        'Total cache misses',
        ['cache_type']
    )

    # 缓存大小
    CACHE_SIZE = Gauge(
        'rag_cache_size',
        'Current cache size',
        ['cache_type']
    )

    # 向量存储文档数
    VECTOR_STORE_DOCS = Gauge(
        'rag_vector_store_docs',
        'Number of documents in vector store',
        ['collection']
    )

    # 活跃对话数
    ACTIVE_CONVERSATIONS = Gauge(
        'rag_active_conversations',
        'Number of active conversations',
        []
    )

    # 系统信息
    SYSTEM_INFO = Info(
        'rag_system',
        'System information'
    )

    # 重排序延迟
    RERANK_LATENCY = Histogram(
        'rag_rerank_latency_seconds',
        'Reranking latency',
        ['method'],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
    )

    # 错误计数
    ERRORS = Counter(
        'rag_errors_total',
        'Total errors',
        ['component', 'error_type']
    )


# ========== 辅助函数 ==========

def setup_system_info(version: str, app_name: str):
    """设置系统信息"""
    if _metrics_enabled and SYSTEM_INFO:
        SYSTEM_INFO.info({
            'version': version,
            'app_name': app_name
        })


def record_request(method: str, endpoint: str, status: int, latency: float):
    """记录 HTTP 请求"""
    if not _metrics_enabled:
        return

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)


def record_retrieval(method: str, latency: float, doc_count: int):
    """记录检索"""
    if not _metrics_enabled:
        return

    RETRIEVAL_LATENCY.labels(method=method).observe(latency)
    RETRIEVAL_DOCS.labels(method=method).observe(doc_count)


def record_llm(model: str, latency: float, input_tokens: int = 0, output_tokens: int = 0):
    """记录 LLM 调用"""
    if not _metrics_enabled:
        return

    LLM_LATENCY.labels(model=model).observe(latency)

    if input_tokens > 0:
        LLM_TOKENS.labels(model=model, type='input').inc(input_tokens)

    if output_tokens > 0:
        LLM_TOKENS.labels(model=model, type='output').inc(output_tokens)


def record_cache_hit(cache_type: str):
    """记录缓存命中"""
    if not _metrics_enabled:
        return

    CACHE_HITS.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """记录缓存未命中"""
    if not _metrics_enabled:
        return

    CACHE_MISSES.labels(cache_type=cache_type).inc()


def update_cache_size(cache_type: str, size: int):
    """更新缓存大小"""
    if not _metrics_enabled:
        return

    CACHE_SIZE.labels(cache_type=cache_type).set(size)


def update_vector_store_docs(collection: str, count: int):
    """更新向量存储文档数"""
    if not _metrics_enabled:
        return

    VECTOR_STORE_DOCS.labels(collection=collection).set(count)


def update_active_conversations(count: int):
    """更新活跃对话数"""
    if not _metrics_enabled:
        return

    ACTIVE_CONVERSATIONS.set(count)


def record_rerank(method: str, latency: float):
    """记录重排序"""
    if not _metrics_enabled:
        return

    RERANK_LATENCY.labels(method=method).observe(latency)


def record_error(component: str, error_type: str):
    """记录错误"""
    if not _metrics_enabled:
        return

    ERRORS.labels(component=component, error_type=error_type).inc()


def get_metrics() -> bytes:
    """获取 Prometheus 指标"""
    if not _metrics_enabled:
        return b"# Prometheus metrics not available (prometheus_client not installed)\n"

    return generate_latest()


# ========== 装饰器 ==========

def track_retrieval(method: str = "vector"):
    """追踪检索性能装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time

                # 尝试获取文档数量
                doc_count = 0
                if isinstance(result, list):
                    doc_count = len(result)
                elif isinstance(result, dict) and 'source_details' in result:
                    doc_count = len(result['source_details'])

                record_retrieval(method, latency, doc_count)
                return result
            except Exception as e:
                record_error('retrieval', type(e).__name__)
                raise
        return wrapper
    return decorator


def track_llm(model: str = "unknown"):
    """追踪 LLM 调用装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time
                record_llm(model, latency)
                return result
            except Exception as e:
                record_error('llm', type(e).__name__)
                raise
        return wrapper
    return decorator


# ========== 中间件 ==========

class PrometheusMiddleware:
    """Prometheus 监控中间件"""

    def __init__(self, app, exclude_paths: list = None):
        """
        初始化中间件

        Args:
            app: FastAPI 应用
            exclude_paths: 排除的路径
        """
        self.app = app
        self.exclude_paths = exclude_paths or ['/metrics', '/health', '/docs', '/openapi.json']

    async def __call__(self, request: Request, call_next: Callable):
        """处理请求"""
        # 排除不需要监控的路径
        path = request.url.path
        if any(path.startswith(exclude) for exclude in self.exclude_paths):
            return await call_next(request)

        # 记录开始时间
        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 计算延迟
        latency = time.time() - start_time

        # 记录指标
        record_request(
            method=request.method,
            endpoint=path,
            status=response.status_code,
            latency=latency
        )

        return response
