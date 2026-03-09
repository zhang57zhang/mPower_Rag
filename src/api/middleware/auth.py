"""
API 认证中间件
支持 API Key 和 Bearer Token 认证
"""
import secrets
from typing import Optional
from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# API Key Header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Bearer Token
bearer_scheme = HTTPBearer(auto_error=False)


class User(BaseModel):
    """用户模型"""
    id: str
    name: str
    role: str = "user"
    api_key: Optional[str] = None


class APIKeyAuth:
    """API Key 认证管理器"""

    def __init__(self, valid_api_keys: list[str], admin_keys: list[str] = None):
        """
        初始化认证管理器

        Args:
            valid_api_keys: 有效的 API Key 列表
            admin_keys: 管理员 API Key 列表
        """
        self.valid_api_keys = set(valid_api_keys or [])
        self.admin_keys = set(admin_keys or [])
        self._key_to_user = {}  # API Key -> User 映射

        # 初始化用户映射
        for i, key in enumerate(self.valid_api_keys):
            role = "admin" if key in self.admin_keys else "user"
            self._key_to_user[key] = User(
                id=f"user_{i}",
                name=f"User {i}",
                role=role,
                api_key=key
            )

    def validate_key(self, api_key: str) -> Optional[User]:
        """
        验证 API Key

        Args:
            api_key: API Key

        Returns:
            用户对象，无效返回 None
        """
        if not api_key:
            return None

        if api_key in self.valid_api_keys:
            return self._key_to_user.get(api_key)

        return None

    def generate_key(self) -> str:
        """
        生成新的 API Key

        Returns:
            新的 API Key
        """
        return f"mpower_{secrets.token_urlsafe(32)}"


# 全局认证管理器（需要在启动时初始化）
_auth_manager: Optional[APIKeyAuth] = None


def init_auth(valid_api_keys: list[str], admin_keys: list[str] = None):
    """
    初始化认证管理器

    Args:
        valid_api_keys: 有效的 API Key 列表
        admin_keys: 管理员 API Key 列表
    """
    global _auth_manager
    _auth_manager = APIKeyAuth(valid_api_keys, admin_keys)
    logger.info(f"认证管理器已初始化，有效 API Key 数量: {len(valid_api_keys)}")


async def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    bearer: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> User:
    """
    验证 API Key 或 Bearer Token

    支持:
    1. X-API-Key Header
    2. Authorization: Bearer <api_key>

    Args:
        request: 请求对象
        api_key: API Key Header
        bearer: Bearer Token

    Returns:
        用户对象

    Raises:
        HTTPException: 认证失败
    """
    if _auth_manager is None:
        # 如果未配置认证，允许所有请求（开发模式）
        logger.warning("认证未配置，允许所有请求（开发模式）")
        return User(id="anonymous", name="Anonymous", role="user")

    # 优先使用 API Key Header
    key = api_key

    # 如果没有 API Key，尝试 Bearer Token
    if not key and bearer:
        key = bearer.credentials

    # 验证 Key
    user = _auth_manager.validate_key(key)

    if user is None:
        logger.warning(f"API Key 验证失败: {key[:10] if key else 'None'}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 将用户信息存储到请求状态
    request.state.user = user

    return user


async def get_current_user(request: Request) -> Optional[User]:
    """
    获取当前用户（可选认证）

    Args:
        request: 请求对象

    Returns:
        用户对象，未认证返回 None
    """
    return getattr(request.state, "user", None)


async def require_admin(user: User = Security(verify_api_key)) -> User:
    """
    要求管理员权限

    Args:
        user: 当前用户

    Returns:
        用户对象

    Raises:
        HTTPException: 权限不足
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


# 白名单路由（不需要认证）
AUTH_WHITELIST = {
    "/health",
    "/health/live",
    "/health/ready",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/metrics",
}


def is_whitelisted(path: str) -> bool:
    """
    检查路径是否在白名单中

    Args:
        path: 请求路径

    Returns:
        是否在白名单
    """
    return path in AUTH_WHITELIST or path.startswith("/docs") or path.startswith("/openapi")
