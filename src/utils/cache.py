"""
Redis 缓存管理器
支持查询缓存、向量检索缓存、LLM 响应缓存
"""
import json
import hashlib
import logging
from typing import Any, Optional, Callable, TypeVar, Union, Dict, List, Iterator
from functools import wraps
import pickle

logger = logging.getLogger(__name__)

# 类型变量
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., T])


class RedisCache:
    """Redis 缓存类"""

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379,
                 redis_db: int = 0, redis_password: Optional[str] = None,
                 redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        初始化 Redis 缓存

        Args:
            redis_host: Redis 主机
            redis_port: Redis 端口
            redis_db: Redis 数据库编号
            redis_password: Redis 密码
            redis_url: Redis 完整 URL（优先使用）
            default_ttl: 默认缓存时间（秒）
        """
        self.default_ttl = default_ttl
        self.redis_client = None

        try:
            if redis_url:
                import redis
                self.redis_client = redis.from_url(redis_url)
                logger.info(f"使用 Redis URL 连接: {redis_url}")
            else:
                import redis
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=False,  # 手动解码
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                logger.info(f"连接 Redis: {redis_host}:{redis_port}/{redis_db}")

            # 测试连接
            self.redis_client.ping()
            logger.info("Redis 连接成功")

        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            self.redis_client = None

    def _generate_key(self, prefix: str, key: Union[str, dict]) -> str:
        """
        生成缓存键

        Args:
            prefix: 键前缀
            key: 键（字符串或字典）

        Returns:
            缓存键
        """
        if isinstance(key, dict):
            # 将字典排序后转换为字符串，确保一致性
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)

        # 使用 MD5 哈希键，避免过长
        hash_obj = hashlib.md5(key_str.encode('utf-8'))
        hash_str = hash_obj.hexdigest()

        return f"{prefix}:{hash_str}"

    def set(self, prefix: str, key: Union[str, dict],
            value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存

        Args:
            prefix: 键前缀
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示使用默认 TTL

        Returns:
            是否设置成功
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_key(prefix, key)
            cache_value = pickle.dumps(value)

            actual_ttl = ttl if ttl is not None else self.default_ttl

            self.redis_client.setex(cache_key, actual_ttl, cache_value)
            logger.debug(f"缓存已设置: {cache_key}, TTL: {actual_ttl}s")
            return True

        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False

    def get(self, prefix: str, key: Union[str, dict]) -> Optional[Any]:
        """
        获取缓存

        Args:
            prefix: 键前缀
            key: 缓存键

        Returns:
            缓存值，不存在或出错返回 None
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_key(prefix, key)
            cache_value = self.redis_client.get(cache_key)

            if cache_value is None:
                logger.debug(f"缓存未命中: {cache_key}")
                return None

            # 解析缓存值
            value = pickle.loads(cache_value)
            logger.debug(f"缓存命中: {cache_key}")
            return value

        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None

    def delete(self, prefix: str, key: Union[str, dict]) -> bool:
        """
        删除缓存

        Args:
            prefix: 键前缀
            key: 缓存键

        Returns:
            是否删除成功
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_key(prefix, key)
            result = self.redis_client.delete(cache_key)
            logger.debug(f"删除缓存: {cache_key}")
            return result > 0

        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False

    def clear_prefix(self, prefix: str) -> int:
        """
        清空指定前缀的所有缓存

        Args:
            prefix: 键前缀

        Returns:
            删除的缓存数量
        """
        if not self.redis_client:
            return 0

        try:
            pattern = f"{prefix}:*"
            keys = self.redis_client.keys(pattern)
            count = 0

            if keys:
                count = self.redis_client.delete(*keys)
                logger.info(f"清空缓存前缀 {prefix}: 删除 {count} 个键")

            return count

        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return 0

    def exists(self, prefix: str, key: Union[str, dict]) -> bool:
        """
        检查缓存是否存在

        Args:
            prefix: 键前缀
            key: 缓存键

        Returns:
            缓存是否存在
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_key(prefix, key)
            return self.redis_client.exists(cache_key) > 0

        except Exception as e:
            logger.error(f"检查缓存存在失败: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "connected": False,
            "total_keys": 0,
            "prefix_counts": {},
        }

        if not self.redis_client:
            return stats

        try:
            # 测试连接
            stats["connected"] = self.redis_client.ping() == "PONG"

            # 获取总键数
            stats["total_keys"] = self.redis_client.dbsize()

            # 获取各前缀的键数
            prefixes = ["query", "retrieval", "llm", "rerank"]
            for prefix in prefixes:
                pattern = f"{prefix}:*"
                keys = self.redis_client.keys(pattern)
                stats["prefix_counts"][prefix] = len(keys)

            return stats

        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return stats


def cache_decorator(cache: RedisCache, prefix: str,
                   ttl: Optional[int] = None, use_args: bool = True,
                   use_kwargs: bool = True, key_func: Optional[Callable] = None):
    """
    Redis 缓存装饰器

    Args:
        cache: Redis 缓存实例
        prefix: 缓存键前缀
        ttl: 缓存 TTL（秒）
        use_args: 是否使用函数参数作为键的一部分
        use_kwargs: 是否使用函数关键字参数作为键的一部分
        key_func: 自定义键生成函数

    Returns:
        装饰器函数
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key_parts = []

                if use_args:
                    cache_key_parts.extend(str(arg) for arg in args)

                if use_kwargs:
                    # 对关键字参数排序，确保键的一致性
                    sorted_kwargs = sorted(kwargs.items())
                    cache_key_parts.extend(f"{k}={v}" for k, v in sorted_kwargs)

                cache_key = ":".join(cache_key_parts)

            # 尝试从缓存获取
            cached_value = cache.get(prefix, cache_key)

            if cached_value is not None:
                logger.info(f"缓存命中: {prefix}:{cache_key[:50]}...")
                return cached_value

            # 缓存未命中，执行函数
            logger.debug(f"缓存未命中: {prefix}:{cache_key[:50]}...，执行函数")
            result = func(*args, **kwargs)

            # 将结果存入缓存
            cache.set(prefix, cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


# 缓存键前缀常量
CACHE_PREFIX_QUERY = "query"           # 查询结果缓存
CACHE_PREFIX_RETRIEVAL = "retrieval"   # 检索结果缓存
CACHE_PREFIX_LLM = "llm"                # LLM 响应缓存
CACHE_PREFIX_RERANK = "rerank"         # 重排序结果缓存


# 全局缓存实例（需要初始化）
_cache_instance: Optional[RedisCache] = None


def get_cache(config: dict) -> Optional[RedisCache]:
    """
    获取缓存实例（单例）

    Args:
        config: 配置字典

    Returns:
        Redis 缓存实例
    """
    global _cache_instance

    if _cache_instance is None:
        if config.get("cache_enabled", False):
            if config.get("cache_type") == "redis":
                _cache_instance = RedisCache(
                    redis_host=config.get("redis_host", "localhost"),
                    redis_port=config.get("redis_port", 6379),
                    redis_db=config.get("redis_db", 0),
                    redis_password=config.get("redis_password"),
                    redis_url=config.get("redis_url"),
                    default_ttl=config.get("cache_ttl", 3600),
                )
                logger.info("Redis 缓存已启用")
            else:
                logger.warning(f"缓存类型 {config.get('cache_type')} 不支持，缓存功能未启用")
        else:
            logger.info("缓存功能未启用")

    return _cache_instance


def clear_all_cache() -> bool:
    """
    清空所有缓存

    Returns:
        是否清空成功
    """
    global _cache_instance

    if _cache_instance is None:
        return False

    try:
        # 清空所有前缀的缓存
        total_cleared = 0
        for prefix in [CACHE_PREFIX_QUERY, CACHE_PREFIX_RETRIEVAL,
                       CACHE_PREFIX_LLM, CACHE_PREFIX_RERANK]:
            total_cleared += _cache_instance.clear_prefix(prefix)

        logger.info(f"已清空所有缓存: {total_cleared} 个键")
        return True

    except Exception as e:
        logger.error(f"清空所有缓存失败: {e}")
        return False
