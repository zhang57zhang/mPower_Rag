"""
嵌入模型配置
支持多种嵌入模型
"""
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Optional


class EmbeddingManager:
    """嵌入模型管理器"""

    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """
        初始化嵌入模型

        Args:
            provider: 提供商 (openai, huggingface)
            model: 模型名称
        """
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.embeddings = self._create_embeddings()

    def _get_default_model(self, provider: str) -> str:
        """获取默认模型"""
        defaults = {
            "openai": "text-embedding-ada-002",
            "huggingface": "shibing624/text2vec-base-chinese",  # 中文优化
        }
        return defaults.get(provider, "text-embedding-ada-002")

    def _create_embeddings(self):
        """创建嵌入模型实例"""
        if self.provider == "openai":
            return OpenAIEmbeddings(
                model=self.model,
                # api_key 和 base_url 从环境变量读取
            )
        elif self.provider == "huggingface":
            return HuggingFaceEmbeddings(
                model_name=self.model,
                model_kwargs={'device': 'cpu'},  # 或 'cuda' 如果有 GPU
            )
        else:
            raise ValueError(f"不支持的嵌入模型提供商: {self.provider}")

    def get_embeddings(self):
        """获取嵌入模型"""
        return self.embeddings


# 全局嵌入模型实例
_embedding_manager = None


def get_embedding_manager(provider: str = "openai", model: Optional[str] = None) -> EmbeddingManager:
    """获取嵌入模型管理器（单例）"""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager(provider, model)
    return _embedding_manager


def get_embeddings(provider: str = "openai", model: Optional[str] = None):
    """获取嵌入模型"""
    manager = get_embedding_manager(provider, model)
    return manager.get_embeddings()
