"""
完全本地的向量检索方案 - 不依赖外部下载
使用TF-IDF + 余弦相似度
"""
from typing import List, Dict, Any, Optional
import logging
import re
import math
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalVectorStore:
    """本地向量存储（无需外部模型）"""

    def __init__(self):
        """初始化本地向量存储"""
        self.documents = []
        self.vocabulary = set()
        self.idf = {}
        self.document_vectors = []
        self.vocab_index = {}

        logger.info("初始化本地向量存储（TF-IDF）")

    def _tokenize(self, text: str) -> List[str]:
        """中文分词（简单版本）"""
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)

        # 简单的按空格和常见中文分词模式
        # 这里使用一个简化方案：按字符和常见词分割
        tokens = []

        # 中文按2字词分割
        for i in range(len(text) - 1):
            if '\u4e00' <= text[i] <= '\u9fff':  # 中文字符
                if '\u4e00' <= text[i+1] <= '\u9fff':
                    tokens.append(text[i:i+2])

        # 英文按单词分割
        words = text.split()
        tokens.extend(words)

        return [t.lower() for t in tokens if len(t) > 1]

    def _build_vocabulary(self, documents: List[str]):
        """构建词汇表"""
        vocab_counter = Counter()

        for doc in documents:
            tokens = self._tokenize(doc)
            vocab_counter.update(tokens)

        # 保留前500个最常见词
        self.vocabulary = set([word for word, count in vocab_counter.most_common(500)])
        self.vocab_index = {word: i for i, word in enumerate(self.vocabulary)}

        # 计算IDF
        total_docs = len(documents)
        for word in self.vocabulary:
            doc_count = sum(1 for doc in documents if word in self._tokenize(doc))
            self.idf[word] = math.log(total_docs / (doc_count + 1)) + 1

        logger.info(f"构建词汇表: {len(self.vocabulary)} 个词")

    def _tfidf_vector(self, text: str) -> List[float]:
        """计算TF-IDF向量"""
        tokens = self._tokenize(text)
        token_counter = Counter(tokens)

        vector = [0.0] * len(self.vocabulary)

        for word, count in token_counter.items():
            if word in self.vocab_index:
                idx = self.vocab_index[word]
                tf = count / len(tokens)
                vector[idx] = tf * self.idf.get(word, 1.0)

        return vector

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """添加文档"""
        try:
            # 提取文档内容
            doc_contents = [doc.get("content", "") for doc in documents]

            # 如果是第一批文档，构建词汇表
            if not self.vocabulary:
                self._build_vocabulary(doc_contents)

            # 计算向量并存储
            for i, doc in enumerate(documents):
                vector = self._tfidf_vector(doc["content"])
                self.documents.append({
                    "id": doc.get("id", len(self.documents)),
                    "content": doc["content"],
                    "source": doc.get("source", ""),
                    "metadata": doc.get("metadata", {})
                })
                self.document_vectors.append(vector)

            logger.info(f"成功添加 {len(documents)} 个文档到本地向量存储")
            return True

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False

    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档ID

        Returns:
            是否删除成功
        """
        try:
            # 查找文档索引
            doc_index = None
            for i, doc in enumerate(self.documents):
                if doc["id"] == doc_id:
                    doc_index = i
                    break

            if doc_index is None:
                logger.warning(f"文档不存在: {doc_id}")
                return False

            # 删除文档和向量
            self.documents.pop(doc_index)
            self.document_vectors.pop(doc_index)

            logger.info(f"成功删除文档: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        if not self.documents:
            return []

        try:
            # 计算查询向量
            query_vector = self._tfidf_vector(query)

            # 计算相似度
            similarities = []
            for i, doc_vector in enumerate(self.document_vectors):
                score = self._cosine_similarity(query_vector, doc_vector)
                similarities.append((i, score))

            # 排序并取top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:top_k]

            # 格式化结果
            results = []
            for idx, score in top_results:
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
        self.document_vectors = []
        self.vocabulary = set()
        self.idf = {}
        self.vocab_index = {}
        logger.info("本地向量存储已清除")

    def get_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        return {
            "document_count": len(self.documents),
            "vector_count": len(self.document_vectors),
            "vocabulary_size": len(self.vocabulary),
            "storage_type": "local_tfidf"
        }
