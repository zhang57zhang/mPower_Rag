"""
缓存管理 API 接口
提供缓存统计、管理等功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from core.utils.cache import get_cache, clear_all_cache, CACHE_PREFIX_QUERY, CACHE_PREFIX_RETRIEVAL, CACHE_PREFIX_LLM, CACHE_PREFIX_RERANK

logger = logging.getLogger(__name__)


class CacheStatsResponse(BaseModel):
    """缓存统计响应模型"""
    enabled: bool = Field(False, description="缓存是否启用")
    connected: bool = Field(False, description="Redis 连接状态")
    total_keys: int = Field(0, description="总键数")
    prefix_counts: Dict[str, int] = Field(default_factory=dict, description="各前缀的键数")


class ClearCacheRequest(BaseModel):
    """清空缓存请求模型"""
    prefix: Optional[str] = Field(None, description="清空指定前缀（query, retrieval, llm, rerank, null 表示全部）")


# 缓存管理函数

_cache_instance = None


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计"""
    global _cache_instance

    if _cache_instance is None:
        from config.settings import settings
        _cache_instance = get_cache(settings.model_dump())

    if _cache_instance is None:
        return {
            "enabled": False,
            "connected": False,
            "total_keys": 0,
            "prefix_counts": {},
        }

    return _cache_instance.get_stats()


def clear_cache(prefix: Optional[str] = None) -> Dict[str, Any]:
    """清空缓存"""
    global _cache_instance

    if _cache_instance is None:
        from config.settings import settings
        _cache_instance = get_cache(settings.model_dump())

    if _cache_instance is None:
        raise HTTPException(status_code=503, detail="缓存未初始化")

    try:
        if prefix:
            # 清空指定前缀
            count = _cache_instance.clear_prefix(prefix)
            return {
                "message": f"已清空前缀 '{prefix}' 的缓存",
                "cleared_count": count,
            }
        else:
            # 清空所有缓存
            count = 0
            for cache_prefix in [CACHE_PREFIX_QUERY, CACHE_PREFIX_RETRIEVAL, CACHE_PREFIX_LLM, CACHE_PREFIX_RERANK]:
                count += _cache_instance.clear_prefix(cache_prefix)

            return {
                "message": f"已清空所有缓存",
                "cleared_count": count,
            }

    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 注意：这些接口应该在 src/api/main.py 中集成
# 由于编辑困难，我创建了这个独立文件，展示如何集成

# 集成示例：
# """
# from fastapi import APIRouter
# from core.api.cache_management import get_cache_stats, clear_cache, CacheStatsResponse, ClearCacheRequest
#
# cache_router = APIRouter(prefix="/api/v1/cache", tags=["cache"])
#
# @cache_router.get("/stats", response_model=CacheStatsResponse)
# async def get_stats_endpoint():
#     return get_cache_stats()
#
# @cache_router.post("/clear")
# async def clear_cache_endpoint(request: ClearCacheRequest):
#     return clear_cache(request.prefix)
#
# 然后在 main.py 中添加：app.include_router(cache_router)
# """
