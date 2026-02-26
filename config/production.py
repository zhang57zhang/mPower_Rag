"""
生产环境配置管理
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class ProductionSettings(BaseSettings):
    """生产环境配置"""

    # 应用信息
    app_name: str = "mPower_Rag"
    app_version: str = "1.0.0"

    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM配置
    llm_provider: str = "deepseek"
    llm_model: str = "deepseek-chat"
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

    # 向量数据库配置
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_collection_name: str = "vehicle_test_knowledge"

    # RAG配置
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5

    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "json"

    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    # 路径配置
    base_dir: Path = Path("/app")
    logs_dir: Path = Path("/app/logs")
    knowledge_base_dir: Path = Path("/app/knowledge_base")
    models_dir: Path = Path("/app/models")
    data_dir: Path = Path("/app/data")

    # 确保目录存在
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 全局配置实例
settings = ProductionSettings()
