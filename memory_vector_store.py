"""
内存向量存储 - 备用方案（当Qdrant不可用时）
使用numpy实现简单的余弦相似度检索
"""
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class MemoryVectorStore:
    """内存向量存储（备用方案）"""

    def __init__(self, embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """初始化内存向量存储"""
        self.documents = []
        self.embeddings = []
        self.embedding_matrix = None

        # 加载嵌入模型
        logger.info(f"正在加载嵌入模型: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)
        logger.info("嵌入模型加载完成")

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """添加文档"""
        try:
            for doc in documents:
                # 生成向量
                embedding = self.model.encode(doc.get("content", ""), convert_to_numpy=True)

                self.documents.append({
                    "id": doc.get("id", len(self.documents)),
                    "content": doc.get("content", ""),
                    "source": doc.get("source", ""),
                    "metadata": doc.get("metadata", {})
                })
                self.embeddings.append(embedding)

            # 构建矩阵
            self.embedding_matrix = np.array(self.embeddings)
            logger.info(f"成功添加 {len(documents)} 个文档到内存向量存储")
            return True

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        if not self.documents:
            return []

        try:
            # 生成查询向量
            query_embedding = self.model.encode(query, convert_to_numpy=True)

            # 计算余弦相似度
            similarities = np.dot(self.embedding_matrix, query_embedding)
            similarities = similarities / (
                np.linalg.norm(self.embedding_matrix, axis=1) * np.linalg.norm(query_embedding)
            )

            # 获取top-k结果
            top_indices = np.argsort(similarities)[::-1][:top_k]

            # 格式化结果
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score >= score_threshold:
                    results.append({
                        "id": self.documents[idx]["id"],
                        "content": self.documents[idx]["content"],
                        "source": self.documents[idx]["source"],
                        "metadata": self.documents[idx]["metadata"],
                        "score": score
                    })

            logger.info(f"搜索查询: '{query}', 找到 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def clear(self):
        """清除所有数据"""
        self.documents = []
        self.embeddings = []
        self.embedding_matrix = None
        logger.info("内存向量存储已清除")

    def get_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        return {
            "document_count": len(self.documents),
            "vector_count": len(self.embeddings),
            "storage_type": "memory",
            "model": self.model.config._name_or_path
        }
