"""
mPower_Rag 配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "mPower_Rag"
    app_version: str = "0.1.0"
    debug: bool = False

    # API 配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # LLM 配置
    llm_provider: str = "glm"  # deepseek, openai, qwen, glm
    llm_model: str = "glm-4-flash"
    llm_api_key: Optional[str] = "10d6cc8dd0194922acefb23f6b82ec7a.x0RZOCgDnrSK1Fvb"
    llm_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    # 向量数据库配置
    vector_db_type: str = "chroma"  # qdrant, chroma
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "vehicle_test_knowledge"
    qdrant_api_key: Optional[str] = None

    # Chroma 持久化路径
    chroma_persist_dir: str = "./data/chroma"

    # RAG 配置
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    retrieval_score_threshold: float = 0.6

    # 重排序配置
    rerank_enabled: bool = False
    rerank_method: str = "cross_encoder"  # cross_encoder, keyword
    rerank_model: str = "BAAI/bge-reranker-base"

    # 缓存配置
    cache_enabled: bool = False
    cache_type: str = "redis"  # redis, memory
    cache_ttl: int = 3600  # 缓存时间（秒），默认 1 小时
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_url: Optional[str] = None  # 完整 URL，优先使用

    # 文档存储路径
    knowledge_base_path: str = "./knowledge_base"
    documents_path: str = "./knowledge_base/documents"
    parsed_data_path: str = "./knowledge_base/parsed"

    # 日志配置
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    # 前端配置
    frontend_port: int = 8501

    # WebSocket 配置
    websocket_max_connections: int = 100

    # ========== 安全配置 ==========

    # API 认证
    api_auth_enabled: bool = False
    api_keys: str = ""  # 逗号分隔的 API Key 列表
    admin_api_keys: str = ""  # 逗号分隔的管理员 API Key 列表

    # CORS
    cors_origins: str = "*"  # 逗号分隔的允许域名列表
    cors_allow_credentials: bool = True

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10

    # 输入限制
    max_content_length: int = 10 * 1024 * 1024  # 10MB
    max_query_length: int = 10000

    # 监控配置
    prometheus_enabled: bool = False
    prometheus_port: int = 9090

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_api_keys(self) -> list:
        """获取 API Key 列表"""
        if not self.api_keys:
            return []
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    def get_admin_api_keys(self) -> list:
        """获取管理员 API Key 列表"""
        if not self.admin_api_keys:
            return []
        return [k.strip() for k in self.admin_api_keys.split(",") if k.strip()]

    def get_cors_origins(self) -> list:
        """获取 CORS 允许的域名列表"""
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# 创建全局配置实例
settings = Settings()
