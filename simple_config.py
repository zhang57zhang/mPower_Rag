"""
简化的配置，移除复杂的LangChain依赖
用于快速测试和基础功能验证
"""
import os
from pathlib import Path
from typing import Optional

# 应用配置
APP_NAME = "mPower_Rag"
APP_VERSION = "1.0.0"
DEBUG = True

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8000

# LLM 配置
LLM_PROVIDER = "deepseek"
LLM_MODEL = "deepseek-chat"
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-0babc66a3dc346c7aaee9d1f507e1821")
LLM_BASE_URL = "https://api.deepseek.com"

# DeepSeek 配置（方便访问）
DEEPSEEK_API_KEY = LLM_API_KEY
DEEPSEEK_BASE_URL = LLM_BASE_URL
DEEPSEEK_MODEL = LLM_MODEL

# 向量数据库配置
VECTOR_DB_TYPE = "qdrant"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "vehicle_test_knowledge"

# RAG 配置
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 5

# 重排序配置
RERANK_ENABLED = True
RERANK_METHOD = "cross_encoder"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# 缓存配置
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1小时

# 日志配置
LOG_LEVEL = "INFO"

# 路径配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

# 确保目录存在
for dir_path in [DATA_DIR, LOGS_DIR, KNOWLEDGE_BASE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def get_env_var(key: str, default: Optional[str] = None) -> str:
    """获取环境变量，支持 .env 文件"""
    return os.getenv(key, default or "")

# 从环境变量覆盖配置
LLM_API_KEY = get_env_var("LLM_API_KEY", LLM_API_KEY)
DEBUG = get_env_var("DEBUG", str(DEBUG)).lower() == "true"

# 创建日志配置
import logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# 模拟的 Document 类（用于测试）
class Document:
    """简化的 Document 类"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"Document(page_content={self.page_content[:50]}..., metadata={self.metadata})"

# 配置类（用于兼容）
class Settings:
    """配置类，模拟原始settings对象"""
    def __init__(self):
        self.app_name = APP_NAME
        self.app_version = APP_VERSION
        self.debug = DEBUG
        self.api_host = API_HOST
        self.api_port = API_PORT
        self.llm_provider = LLM_PROVIDER
        self.llm_model = LLM_MODEL
        self.llm_api_key = LLM_API_KEY
        self.llm_base_url = LLM_BASE_URL
        self.vector_db_type = VECTOR_DB_TYPE
        self.qdrant_host = QDRANT_HOST
        self.qdrant_port = QDRANT_PORT
        self.qdrant_collection = QDRANT_COLLECTION_NAME
        self.QDRANT_HOST = QDRANT_HOST
        self.QDRANT_PORT = QDRANT_PORT
        self.QDRANT_COLLECTION_NAME = QDRANT_COLLECTION_NAME
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
        self.top_k = TOP_K
        self.rerank_enabled = RERANK_ENABLED
        self.rerank_method = RERANK_METHOD
        self.rerank_model = RERANK_MODEL
        self.cache_enabled = CACHE_ENABLED
        self.cache_ttl = CACHE_TTL
        self.log_level = LOG_LEVEL
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR
        self.knowledge_base_dir = KNOWLEDGE_BASE_DIR
        # Add LLM aliases for compatibility
        self.LLM_PROVIDER = LLM_PROVIDER
        self.LLM_MODEL = LLM_MODEL
        self.LLM_API_KEY = LLM_API_KEY
        self.LLM_BASE_URL = LLM_BASE_URL
        # 添加常用的属性别名（兼容性）
        self.APP_NAME = APP_NAME
        self.APP_VERSION = APP_VERSION
        self.API_HOST = API_HOST
        self.API_PORT = API_PORT
        self.LOG_LEVEL = LOG_LEVEL
        self.TOP_K = TOP_K
        self.CACHE_ENABLED = CACHE_ENABLED
        self.CHUNK_SIZE = CHUNK_SIZE
        self.RERANK_ENABLED = RERANK_ENABLED
        # DeepSeek aliases
        self.DEEPSEEK_API_KEY = DEEPSEEK_API_KEY
        self.DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL
        self.DEEPSEEK_MODEL = DEEPSEEK_MODEL

# 创建settings实例
settings = Settings()

# 模拟的 Document 类（用于测试）
class Document:
    """简化的 Document 类"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Document(page_content={self.page_content[:50]}..., metadata={self.metadata})"