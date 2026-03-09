"""
Rate Limiting 中间件
基于 IP 和 API Key 的请求限流
"""
import time
from typing import Callable, Optional
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class RateLimitConfig(BaseModel):
    """限流配置"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # 突发请求大小


class TokenBucket:
    """令牌桶算法实现"""

    def __init__(self, rate: float, burst_size: int):
        """
        初始化令牌桶

        Args:
            rate: 每秒添加的令牌数
            burst_size: 桶的最大容量
        """
        self.rate = rate
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌

        Args:
            tokens: 需要消费的令牌数

        Returns:
            是否成功消费
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now

            # 添加令牌
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.rate
            )

            # 消费令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        获取需要等待的时间

        Args:
            tokens: 需要的令牌数

        Returns:
            需要等待的秒数
        """
        with self.lock:
            if self.tokens >= tokens:
                return 0.0
            needed = tokens - self.tokens
            return needed / self.rate


class RateLimiter:
    """请求限流器"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
        enabled: bool = True
    ):
        """
        初始化限流器

        Args:
            requests_per_minute: 每分钟请求数限制
            requests_per_hour: 每小时请求数限制
            burst_size: 突发请求大小
            enabled: 是否启用限流
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        self.enabled = enabled

        # IP -> TokenBucket 映射
        self._ip_buckets: dict[str, TokenBucket] = {}
        # API Key -> TokenBucket 映射
        self._key_buckets: dict[str, TokenBucket] = {}

        # 清理锁
        self._cleanup_lock = Lock()
        self._last_cleanup = time.time()

        # 速率（每秒请求数）
        self._rate = requests_per_minute / 60.0

    def _get_ip_bucket(self, ip: str) -> TokenBucket:
        """
        获取 IP 对应的令牌桶

        Args:
            ip: 客户端 IP

        Returns:
            令牌桶
        """
        if ip not in self._ip_buckets:
            self._ip_buckets[ip] = TokenBucket(
                rate=self._rate,
                burst_size=self.burst_size
            )
        return self._ip_buckets[ip]

    def _get_key_bucket(self, api_key: str) -> TokenBucket:
        """
        获取 API Key 对应的令牌桶

        Args:
            api_key: API Key

        Returns:
            令牌桶
        """
        if api_key not in self._key_buckets:
            self._key_buckets[api_key] = TokenBucket(
                rate=self._rate,
                burst_size=self.burst_size
            )
        return self._key_buckets[api_key]

    def _cleanup_old_buckets(self):
        """
        清理长时间未使用的令牌桶
        """
        now = time.time()
        if now - self._last_cleanup < 3600:  # 每小时清理一次
            return

        with self._cleanup_lock:
            if now - self._last_cleanup < 3600:
                return

            # 清理超过 1 小时未使用的桶
            threshold = now - 3600

            # 清理 IP 桶
            ips_to_remove = []
            for ip, bucket in self._ip_buckets.items():
                if bucket.last_update < threshold:
                    ips_to_remove.append(ip)
            for ip in ips_to_remove:
                del self._ip_buckets[ip]

            # 清理 API Key 桶
            keys_to_remove = []
            for key, bucket in self._key_buckets.items():
                if bucket.last_update < threshold:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._key_buckets[key]

            self._last_cleanup = now
            logger.info(f"清理了 {len(ips_to_remove)} 个 IP 桶，{len(keys_to_remove)} 个 API Key 桶")

    def check_rate_limit(
        self,
        ip: str,
        api_key: Optional[str] = None
    ) -> tuple[bool, dict]:
        """
        检查是否超过限流

        Args:
            ip: 客户端 IP
            api_key: API Key（可选）

        Returns:
            (是否允许, 限流信息)
        """
        if not self.enabled:
            return True, {}

        self._cleanup_old_buckets()

        # 优先检查 API Key 限流
        if api_key:
            bucket = self._get_key_bucket(api_key)
            if not bucket.consume():
                wait_time = bucket.get_wait_time()
                return False, {
                    "reason": "api_key_rate_limit",
                    "retry_after": int(wait_time) + 1,
                    "limit": self.requests_per_minute,
                    "window": "minute"
                }

        # 检查 IP 限流
        ip_bucket = self._get_ip_bucket(ip)
        if not ip_bucket.consume():
            wait_time = ip_bucket.get_wait_time()
            return False, {
                "reason": "ip_rate_limit",
                "retry_after": int(wait_time) + 1,
                "limit": self.requests_per_minute,
                "window": "minute"
            }

        return True, {}

    async def __call__(self, request: Request, call_next: Callable):
        """
        中间件调用

        Args:
            request: 请求对象
            call_next: 下一个中间件

        Returns:
            响应
        """
        # 获取客户端 IP
        ip = self._get_client_ip(request)

        # 获取 API Key（如果有）
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                api_key = auth[7:]

        # 检查限流
        allowed, info = self.check_rate_limit(ip, api_key)

        if not allowed:
            logger.warning(f"限流触发: IP={ip}, API Key={api_key[:10] if api_key else 'None'}, Info={info}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(info.get("limit", 60)),
                    "X-RateLimit-Window": info.get("window", "minute")
                }
            )

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实 IP

        Args:
            request: 请求对象

        Returns:
            客户端 IP
        """
        # 检查代理头
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 直接连接
        if request.client:
            return request.client.host

        return "unknown"


# 全局限流器实例
_rate_limiter: Optional[RateLimiter] = None


def init_rate_limiter(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    burst_size: int = 10,
    enabled: bool = True
):
    """
    初始化全局限流器

    Args:
        requests_per_minute: 每分钟请求数限制
        requests_per_hour: 每小时请求数限制
        burst_size: 突发请求大小
        enabled: 是否启用
    """
    global _rate_limiter
    _rate_limiter = RateLimiter(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        burst_size=burst_size,
        enabled=enabled
    )
    logger.info(f"限流器已初始化: {requests_per_minute} req/min, burst={burst_size}, enabled={enabled}")


def get_rate_limiter() -> Optional[RateLimiter]:
    """
    获取全局限流器

    Returns:
        限流器实例
    """
    return _rate_limiter
