"""
健康检查模块
提供完整的服务健康检查接口
"""
import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str  # healthy, unhealthy, degraded
    timestamp: str
    version: str = "1.0.0"
    uptime_seconds: float
    checks: Dict[str, Any]


class DependencyHealth(BaseModel):
    """依赖服务健康状态"""
    name: str
    status: str
    latency_ms: float
    details: Dict[str, Any] = {}


# 应用启动时间
START_TIME = time.time()


async def check_qdrant_health() -> DependencyHealth:
    """
    检查 Qdrant 健康状态
    
    Returns:
        Qdrant 健康状态
    """
    start = time.time()
    try:
        from qdrant_client import QdrantClient
        from config.settings import settings
        
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=getattr(settings, "qdrant_api_key", None),
            timeout=5
        )
        
        # 尝试获取集合信息
        collections = client.get_collections()
        latency = (time.time() - start) * 1000
        
        return DependencyHealth(
            name="qdrant",
            status="healthy",
            latency_ms=round(latency, 2),
            details={
                "collections_count": len(collections.collections),
                "host": settings.qdrant_host,
                "port": settings.qdrant_port
            }
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        logger.error(f"Qdrant 健康检查失败: {e}")
        return DependencyHealth(
            name="qdrant",
            status="unhealthy",
            latency_ms=round(latency, 2),
            details={"error": str(e)}
        )


async def check_redis_health() -> DependencyHealth:
    """
    检查 Redis 健康状态
    
    Returns:
        Redis 健康状态
    """
    start = time.time()
    try:
        import redis
        from config.settings import settings
        
        if not settings.cache_enabled:
            return DependencyHealth(
                name="redis",
                status="disabled",
                latency_ms=0,
                details={"message": "Cache disabled"}
            )
        
        # 连接 Redis
        if settings.redis_url:
            client = redis.from_url(settings.redis_url)
        else:
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                socket_timeout=5
            )
        
        # 执行 PING 命令
        result = client.ping()
        latency = (time.time() - start) * 1000
        
        # 获取 Redis 信息
        info = client.info("memory")
        
        return DependencyHealth(
            name="redis",
            status="healthy" if result else "unhealthy",
            latency_ms=round(latency, 2),
            details={
                "used_memory": info.get("used_memory_human", "unknown"),
                "maxmemory": info.get("maxmemory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        logger.error(f"Redis 健康检查失败: {e}")
        return DependencyHealth(
            name="redis",
            status="unhealthy",
            latency_ms=round(latency, 2),
            details={"error": str(e)}
        )


async def check_llm_health() -> DependencyHealth:
    """
    检查 LLM 服务健康状态
    
    Returns:
        LLM 健康状态
    """
    start = time.time()
    try:
        import httpx
        from config.settings import settings
        
        # 简单的 API 连接检查（不消耗 token）
        async with httpx.AsyncClient(timeout=10) as client:
            # 尝试访问 API 基础 URL
            response = await client.get(
                f"{settings.llm_base_url}/models",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                timeout=5
            )
            
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return DependencyHealth(
                    name="llm",
                    status="healthy",
                    latency_ms=round(latency, 2),
                    details={
                        "provider": settings.llm_provider,
                        "model": settings.llm_model,
                        "base_url": settings.llm_base_url
                    }
                )
            else:
                return DependencyHealth(
                    name="llm",
                    status="unhealthy",
                    latency_ms=round(latency, 2),
                    details={
                        "error": f"API returned {response.status_code}",
                        "provider": settings.llm_provider
                    }
                )
    except Exception as e:
        latency = (time.time() - start) * 1000
        logger.error(f"LLM 健康检查失败: {e}")
        return DependencyHealth(
            name="llm",
            status="unhealthy",
            latency_ms=round(latency, 2),
            details={"error": str(e)}
        )


async def check_disk_space() -> DependencyHealth:
    """
    检查磁盘空间
    
    Returns:
        磁盘空间状态
    """
    try:
        import shutil
        from config.settings import settings
        
        # 检查知识库目录磁盘空间
        total, used, free = shutil.disk_usage(settings.knowledge_base_path)
        free_percent = (free / total) * 100
        
        status = "healthy" if free_percent > 20 else "degraded" if free_percent > 10 else "unhealthy"
        
        return DependencyHealth(
            name="disk",
            status=status,
            latency_ms=0,
            details={
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "free_percent": round(free_percent, 2)
            }
        )
    except Exception as e:
        logger.error(f"磁盘空间检查失败: {e}")
        return DependencyHealth(
            name="disk",
            status="unknown",
            latency_ms=0,
            details={"error": str(e)}
        )


@router.get("/health/live", summary="存活检查")
async def liveness_check():
    """
    Kubernetes 存活检查
    
    如果返回 200，说明服务正在运行
    """
    return {"status": "alive"}


@router.get("/health/ready", summary="就绪检查")
async def readiness_check():
    """
    Kubernetes 就绪检查
    
    检查服务是否准备好接收流量
    """
    # 检查核心依赖
    checks = await asyncio.gather(
        check_qdrant_health(),
        check_llm_health()
    )
    
    # 如果任一核心依赖不健康，返回 503
    unhealthy = [c for c in checks if c.status == "unhealthy"]
    if unhealthy:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "unhealthy_dependencies": [c.name for c in unhealthy]
            }
        )
    
    return {"status": "ready"}


@router.get("/health", response_model=HealthStatus, summary="完整健康检查")
async def health_check():
    """
    完整的健康检查
    
    返回所有依赖服务的健康状态
    """
    # 并发执行所有健康检查
    checks_list = await asyncio.gather(
        check_qdrant_health(),
        check_redis_health(),
        check_llm_health(),
        check_disk_space()
    )
    
    # 转换为字典
    checks = {check.name: check.dict() for check in checks_list}
    
    # 确定整体状态
    statuses = [check.status for check in checks_list]
    
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
    elif "degraded" in statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    # 计算运行时间
    uptime = time.time() - START_TIME
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=round(uptime, 2),
        checks=checks
    )


@router.get("/health/startup", summary="启动检查")
async def startup_check():
    """
    Kubernetes 启动检查
    
    检查应用是否已完成启动
    """
    # 检查是否已初始化
    # 可以根据实际需求添加更多检查
    return {"status": "started"}
