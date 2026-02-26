"""
向量数据库管理
支持 Qdrant 和 Chroma
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain.vectorstores import Qdrant as LCQdrant
from langchain.vectorstores import Chroma
from langchain_core.documents import Document
import uuid


class VectorStoreManager:
    """向量数据库管理器"""

    def __init__(
        self,
        db_type: str = "qdrant",
        collection_name: str = "default",
        embeddings=None,
        **kwargs
    ):
        """
        初始化向量数据库

        Args:
            db_type: 数据库类型 (qdrant, chroma)
            collection_name: 集合名称
            embeddings: 嵌入模型
            **kwargs: 其他配置参数
        """
        self.db_type = db_type
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.kwargs = kwargs
        self.vector_store = self._create_vector_store()

    def _create_vector_store(self):
        """创建向量存储实例"""
        if self.db_type == "qdrant":
            return self._create_qdrant()
        elif self.db_type == "chroma":
            return self._create_chroma()
        else:
            raise ValueError(f"不支持的向量数据库类型: {self.db_type}")

    def _create_qdrant(self):
        """创建 Qdrant 向量存储"""
        client = QdrantClient(
            host=self.kwargs.get("host", "localhost"),
            port=self.kwargs.get("port", 6333),
            api_key=self.kwargs.get("api_key"),
        )

        # 检查并创建集合
        self._ensure_qdrant_collection(client)

        return LCQdrant(
            client=client,
            collection_name=self.collection_name,
            embeddings=self.embeddings,
        )

    def _ensure_qdrant_collection(self, client: QdrantClient):
        """确保 Qdrant 集合存在"""
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI embedding 维度
                    distance=Distance.COSINE,
                ),
            )

    def _create_chroma(self):
        """创建 Chroma 向量存储"""
        persist_dir = self.kwargs.get("persist_dir", "./data/chroma")
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
        )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        添加文档到向量库

        Args:
            documents: 文档列表

        Returns:
            添加的文档 ID 列表
        """
        ids = self.vector_store.add_documents(documents)
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件
            score_threshold: 相似度阈值

        Returns:
            相关文档列表
        """
        if self.db_type == "qdrant":
            return self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter,
                score_threshold=score_threshold,
            )
        else:
            # Chroma 可能不支持所有参数
            return self.vector_store.similarity_search(
                query=query,
                k=k,
            )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """
        相似度搜索（带分数）

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            (文档, 相似度分数) 元组列表
        """
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
        )

    def delete(self, ids: List[str]):
        """
        删除文档

        Args:
            ids: 要删除的文档 ID 列表
        """
        if self.db_type == "qdrant":
            self.vector_store.delete(ids)
        else:
            # Chroma 删除方式
            self.vector_store.delete(ids)

    def clear(self):
        """清空所有文档"""
        if self.db_type == "qdrant":
            client = QdrantClient(
                host=self.kwargs.get("host", "localhost"),
                port=self.kwargs.get("port", 6333),
                api_key=self.kwargs.get("api_key"),
            )
            client.delete_collection(self.collection_name)
        else:
            self.vector_store.delete_collection()


# 全局向量存储实例
_vector_store = None


def get_vector_store(
    db_type: str = "qdrant",
    collection_name: str = "default",
    embeddings=None,
    **kwargs
) -> VectorStoreManager:
    """获取向量存储管理器（单例）"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreManager(
            db_type=db_type,
            collection_name=collection_name,
            embeddings=embeddings,
            **kwargs
        )
    return _vector_store
