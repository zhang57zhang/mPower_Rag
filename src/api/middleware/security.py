"""
安全中间件
CORS 配置、安全头、输入验证
"""
from typing import Callable, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import re

logger = logging.getLogger(__name__)


class SecurityConfig(BaseModel):
    """安全配置"""
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # 安全头
    enable_security_headers: bool = True
    content_security_policy: Optional[str] = None
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"

    # 输入验证
    max_content_length: int = 10 * 1024 * 1024  # 10MB
    max_query_length: int = 10000
    blocked_patterns: List[str] = [
        # SQL 注入模式
        r"(?i)(union\s+select|insert\s+into|delete\s+from|drop\s+table)",
        # XSS 模式
        r"(?i)(<script|javascript:|onerror\s*=|onload\s*=)",
    ]


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""

    def __init__(self, app, config: SecurityConfig = None):
        """
        初始化安全中间件

        Args:
            app: FastAPI 应用
            config: 安全配置
        """
        super().__init__(app)
        self.config = config or SecurityConfig()
        self._compiled_patterns = [
            re.compile(p) for p in self.config.blocked_patterns
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求

        Args:
            request: 请求对象
            call_next: 下一个处理器

        Returns:
            响应
        """
        # 检查内容长度
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.config.max_content_length:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )

        # 检查查询参数
        query_string = str(request.query_params)
        if len(query_string) > self.config.max_query_length:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=414,
                content={"detail": "Query string too long"}
            )

        # 检查恶意模式
        if self._check_malicious_patterns(query_string):
            logger.warning(f"检测到可疑请求: {request.client.host if request.client else 'unknown'}")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )

        # 调用下一个处理器
        response = await call_next(request)

        # 添加安全头
        if self.config.enable_security_headers:
            self._add_security_headers(response)

        return response

    def _check_malicious_patterns(self, text: str) -> bool:
        """
        检查恶意模式

        Args:
            text: 待检查文本

        Returns:
            是否包含恶意模式
        """
        for pattern in self._compiled_patterns:
            if pattern.search(text):
                return True
        return False

    def _add_security_headers(self, response: Response):
        """
        添加安全头

        Args:
            response: 响应对象
        """
        headers = response.headers

        # X-Frame-Options
        if self.config.x_frame_options:
            headers["X-Frame-Options"] = self.config.x_frame_options

        # X-Content-Type-Options
        if self.config.x_content_type_options:
            headers["X-Content-Type-Options"] = self.config.x_content_type_options

        # X-XSS-Protection
        if self.config.x_xss_protection:
            headers["X-XSS-Protection"] = self.config.x_xss_protection

        # Strict-Transport-Security (HTTPS)
        if self.config.strict_transport_security:
            headers["Strict-Transport-Security"] = self.config.strict_transport_security

        # Content-Security-Policy
        if self.config.content_security_policy:
            headers["Content-Security-Policy"] = self.config.content_security_policy

        # 防止缓存敏感信息
        headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        headers["Pragma"] = "no-cache"


def create_cors_middleware(
    allow_origins: List[str] = None,
    allow_credentials: bool = True,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
) -> CORSMiddleware:
    """
    创建 CORS 中间件配置

    Args:
        allow_origins: 允许的域名列表
        allow_credentials: 是否允许凭证
        allow_methods: 允许的方法
        allow_headers: 允许的头

    Returns:
        CORS 中间件配置
    """
    config = SecurityConfig(
        cors_origins=allow_origins or ["*"],
        cors_allow_credentials=allow_credentials,
        cors_allow_methods=allow_methods or ["*"],
        cors_allow_headers=allow_headers or ["*"],
    )

    return dict(
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )


# 白名单路径（跳过安全检查）
SECURITY_WHITELIST = {
    "/health",
    "/health/live",
    "/health/ready",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
}
