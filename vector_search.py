"""
向量检索模块 - 三层fallback机制
优先级: Qdrant > sentence-transformers > 本地TF-IDF
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VectorSearchEngine:
    """向量搜索引擎（三层fallback）"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents",
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        vector_size: int = 384,
        use_local_fallback: bool = True
    ):
        """初始化向量搜索引擎"""
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.use_local_fallback = use_local_fallback

        # 尝试三层方案
        self.backend = None
        self.backend_type = None

        if self._try_qdrant():
            self.backend_type = "qdrant"
            logger.info("使用 Qdrant 向量数据库")
        elif self._try_sentence_transformers(embedding_model):
            self.backend_type = "sentence_transformers"
            logger.info("使用 sentence-transformers (内存)")
        elif use_local_fallback:
            self._use_local_store()
            self.backend_type = "local_tfidf"
            logger.info("使用本地 TF-IDF 向量存储")
        else:
            raise Exception("所有向量检索方案都不可用")

    def _try_qdrant(self) -> bool:
        """尝试使用Qdrant"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            client = QdrantClient(host=self.host, port=self.port)
            client.get_collections()

            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"创建集合: {self.collection_name}")
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )

            self._qdrant_client = client
            return True

        except Exception as e:
            logger.debug(f"Qdrant不可用: {e}")
            return False

    def _try_sentence_transformers(self, model_name: str) -> bool:
        """尝试使用sentence-transformers"""
        try:
            from memory_vector_store import MemoryVectorStore
            self._memory_store = MemoryVectorStore(model_name)
            # 测试编码
            test = self._memory_store.model.encode("test", convert_to_numpy=False)
            return True
        except Exception as e:
            logger.debug(f"sentence-transformers不可用: {e}")
            return False

    def _use_local_store(self):
        """使用本地TF-IDF存储"""
        from local_vector_store import LocalVectorStore
        self._local_store = LocalVectorStore()

    def encode_text(self, text: str) -> List[float]:
        """将文本编码为向量"""
        if self.backend_type == "local_tfidf":
            return self._local_store._tfidf_vector(text)
        else:
            raise NotImplementedError(f"encode_text for {self.backend_type}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """添加文档"""
        if self.backend_type == "qdrant":
            return self._add_documents_qdrant(documents)
        elif self.backend_type == "sentence_transformers":
            return self._memory_store.add_documents(documents)
        else:
            return self._local_store.add_documents(documents)

    def _add_documents_qdrant(self, documents: List[Dict[str, Any]]) -> bool:
        """添加文档到Qdrant"""
        try:
            from qdrant_client.models import PointStruct
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            points = []

            for i, doc in enumerate(documents):
                vector = model.encode(doc.get("content", ""), convert_to_numpy=False).tolist()

                point = PointStruct(
                    id=doc.get("id", i),
                    vector=vector,
                    payload={
                        "content": doc.get("content", ""),
                        "source": doc.get("source", ""),
                        **doc.get("metadata", {})
                    }
                )
                points.append(point)

            self._qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"成功添加 {len(points)} 个文档到Qdrant")
            return True

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.1,  # 降低默认阈值
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        if self.backend_type == "qdrant":
            return self._search_qdrant(query, top_k, score_threshold, filters)
        elif self.backend_type == "sentence_transformers":
            return self._memory_store.search(query, top_k, score_threshold)
        else:
            return self._local_store.search(query, top_k, score_threshold)

    def _search_qdrant(self, query: str, top_k: int, score_threshold: float, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """在Qdrant中搜索"""
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            query_vector = model.encode(query, convert_to_numpy=False).tolist()

            results = self._qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold
            )

            documents = []
            for result in results:
                documents.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "source": result.payload.get("source", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k not in ["content", "source"]},
                    "score": result.score
                })

            logger.info(f"搜索查询: '{query}', 找到 {len(documents)} 个结果")
            return documents

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        if self.backend_type == "local_tfidf":
            info = self._local_store.get_info()
            return {
                "name": "local_tfidf_store",
                "backend": "local_tfidf",
                **info
            }
        elif self.backend_type == "sentence_transformers":
            info = self._memory_store.get_info()
            return {
                "name": "memory_store",
                "backend": "sentence_transformers",
                **info
            }
        else:
            try:
                info = self._qdrant_client.get_collection(self.collection_name)
                return {
                    "name": self.collection_name,
                    "backend": "qdrant",
                    "vectors_count": info.vectors_count,
                    "indexed_vectors_count": info.indexed_vectors_count,
                    "points_count": info.points_count,
                    "status": info.status
                }
            except Exception as e:
                logger.error(f"获取集合信息失败: {e}")
                return {}
