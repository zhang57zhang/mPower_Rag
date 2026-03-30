"""
混合检索模块
结合向量检索和 BM25 关键词检索
"""
import logging
import math
from typing import List, Dict, Any, Tuple, Optional, Iterator
from collections import Counter
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果"""
    content: str
    metadata: Dict[str, Any]
    vector_score: float = 0.0
    bm25_score: float = 0.0
    combined_score: float = 0.0


class BM25:
    """BM25 关键词检索实现"""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        language: str = "chinese"
    ):
        """
        初始化 BM25

        Args:
            k1: 词频饱和参数
            b: 文档长度归一化参数
            language: 语言（chinese/english）
        """
        self.k1 = k1
        self.b = b
        self.language = language

        # 文档库
        self.documents: List[str] = []
        self.doc_metadata: List[Dict[str, Any]] = []

        # 分词后的文档
        self.tokenized_docs: List[List[str]] = []

        # BM25 参数
        self.doc_count = 0
        self.avg_doc_length = 0.0
        self.doc_lengths: List[int] = []
        self.idf: Dict[str, float] = {}
        self.doc_term_freqs: List[Dict[str, int]] = []

        # 是否已索引
        self._indexed = False

    def _tokenize(self, text: str) -> List[str]:
        """
        分词

        Args:
            text: 待分词文本

        Returns:
            词项列表
        """
        if self.language == "chinese":
            try:
                import jieba
                # 使用 jieba 分词
                tokens = list(jieba.cut(text))
                # 过滤停用词和标点
                tokens = [t.strip() for t in tokens if len(t.strip()) > 1]
            except ImportError:
                # 降级为字符级分词
                tokens = [c for c in text if c.strip() and len(c.strip()) > 0]
                logger.warning("jieba 未安装，使用字符级分词")
        else:
            # 英文分词
            tokens = re.findall(r'\b\w+\b', text.lower())

        return tokens

    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """
        添加文档到索引

        Args:
            documents: 文档列表
            metadata: 元数据列表
        """
        if metadata is None:
            metadata = [{}] * len(documents)

        self.documents.extend(documents)
        self.doc_metadata.extend(metadata)

        # 分词
        for doc in documents:
            tokens = self._tokenize(doc)
            self.tokenized_docs.append(tokens)
            self.doc_lengths.append(len(tokens))

        self._indexed = False
        logger.info(f"BM25 添加了 {len(documents)} 个文档")

    def build_index(self):
        """构建 BM25 索引"""
        if self._indexed:
            return

        self.doc_count = len(self.documents)
        if self.doc_count == 0:
            return

        # 计算平均文档长度
        self.avg_doc_length = sum(self.doc_lengths) / self.doc_count

        # 计算每个文档的词项频率
        self.doc_term_freqs = []
        for tokens in self.tokenized_docs:
            term_freq = Counter(tokens)
            self.doc_term_freqs.append(dict(term_freq))

        # 计算 IDF
        doc_freqs: Dict[str, int] = Counter()
        for term_freq in self.doc_term_freqs:
            for term in term_freq:
                doc_freqs[term] += 1

        for term, df in doc_freqs.items():
            # IDF 公式: log((N - df + 0.5) / (df + 0.5) + 1)
            self.idf[term] = math.log(
                (self.doc_count - df + 0.5) / (df + 0.5) + 1
            )

        self._indexed = True
        logger.info(f"BM25 索引构建完成，文档数: {self.doc_count}, 词项数: {len(self.idf)}")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        搜索

        Args:
            query: 查询文本
            top_k: 返回数量

        Returns:
            (文档索引, 分数) 列表
        """
        if not self._indexed:
            self.build_index()

        if self.doc_count == 0:
            return []

        # 分词
        query_tokens = self._tokenize(query)
        query_term_freq = Counter(query_tokens)

        # 计算每个文档的 BM25 分数
        scores = []
        for doc_idx, doc_term_freq in enumerate(self.doc_term_freqs):
            score = 0.0
            doc_length = self.doc_lengths[doc_idx]

            for term, query_freq in query_term_freq.items():
                if term not in self.idf:
                    continue

                # 文档中该词的频率
                doc_freq = doc_term_freq.get(term, 0)
                if doc_freq == 0:
                    continue

                # BM25 公式
                idf = self.idf[term]
                numerator = doc_freq * (self.k1 + 1)
                denominator = doc_freq + self.k1 * (
                    1 - self.b + self.b * (doc_length / self.avg_doc_length)
                )
                score += idf * (numerator / denominator)

            if score > 0:
                scores.append((doc_idx, score))

        # 排序
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]

    def get_document(self, doc_idx: int) -> Tuple[str, Dict[str, Any]]:
        """
        获取文档

        Args:
            doc_idx: 文档索引

        Returns:
            (文档内容, 元数据)
        """
        if 0 <= doc_idx < len(self.documents):
            return self.documents[doc_idx], self.doc_metadata[doc_idx]
        return "", {}


class HybridSearch:
    """混合检索：向量检索 + BM25"""

    def __init__(
        self,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75,
        language: str = "chinese"
    ):
        """
        初始化混合检索

        Args:
            vector_weight: 向量检索权重
            bm25_weight: BM25 权重
            bm25_k1: BM25 k1 参数
            bm25_b: BM25 b 参数
            language: 语言
        """
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight

        # BM25 检索器
        self.bm25 = BM25(k1=bm25_k1, b=bm25_b, language=language)

        logger.info(f"混合检索初始化: vector_weight={vector_weight}, bm25_weight={bm25_weight}")

    def add_documents(
        self,
        documents: List[str],
        metadata: List[Dict[str, Any]] = None
    ):
        """
        添加文档

        Args:
            documents: 文档列表
            metadata: 元数据列表
        """
        self.bm25.add_documents(documents, metadata)

    def build_index(self):
        """构建索引"""
        self.bm25.build_index()

    def search(
        self,
        query: str,
        vector_results: List[Tuple[str, Dict[str, Any], float]],
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        混合搜索

        Args:
            query: 查询文本
            vector_results: 向量检索结果 [(content, metadata, score), ...]
            top_k: 返回数量

        Returns:
            混合检索结果
        """
        # BM25 检索
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        # 构建 BM25 分数映射
        bm25_scores: Dict[int, float] = {}
        bm25_max_score = max((s for _, s in bm25_results), default=1.0)

        for doc_idx, score in bm25_results:
            # 归一化 BM25 分数
            bm25_scores[doc_idx] = score / bm25_max_score if bm25_max_score > 0 else 0

        # 构建向量分数映射
        vector_scores: Dict[str, float] = {}
        vector_max_score = max((s for _, _, s in vector_results), default=1.0)

        for content, _, score in vector_results:
            # 使用内容哈希作为键
            content_hash = str(hash(content))
            # 归一化向量分数
            vector_scores[content_hash] = score / vector_max_score if vector_max_score > 0 else 0

        # 合并结果
        combined_results: Dict[str, SearchResult] = {}

        # 处理向量检索结果
        for content, metadata, vec_score in vector_results:
            content_hash = str(hash(content))
            norm_vec_score = vector_scores.get(content_hash, 0)

            # 查找对应的 BM25 分数
            bm25_score = 0.0
            for doc_idx, (doc_content, _) in enumerate(
                [(self.bm25.documents[i], self.bm25.doc_metadata[i])
                 for i in range(len(self.bm25.documents))]
            ):
                if doc_content == content:
                    bm25_score = bm25_scores.get(doc_idx, 0)
                    break

            # 计算组合分数
            combined_score = (
                self.vector_weight * norm_vec_score +
                self.bm25_weight * bm25_score
            )

            combined_results[content_hash] = SearchResult(
                content=content,
                metadata=metadata,
                vector_score=norm_vec_score,
                bm25_score=bm25_score,
                combined_score=combined_score
            )

        # 处理仅 BM25 检索到的结果
        for doc_idx, bm25_score in bm25_results[:top_k]:
            content, metadata = self.bm25.get_document(doc_idx)
            content_hash = str(hash(content))

            if content_hash not in combined_results:
                norm_bm25_score = bm25_scores.get(doc_idx, 0)

                combined_score = self.bm25_weight * norm_bm25_score

                combined_results[content_hash] = SearchResult(
                    content=content,
                    metadata=metadata,
                    vector_score=0.0,
                    bm25_score=norm_bm25_score,
                    combined_score=combined_score
                )

        # 排序并返回 top_k
        results = list(combined_results.values())
        results.sort(key=lambda x: x.combined_score, reverse=True)

        return results[:top_k]

    def update_weights(self, vector_weight: float, bm25_weight: float):
        """
        更新权重

        Args:
            vector_weight: 向量检索权重
            bm25_weight: BM25 权重
        """
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        logger.info(f"权重已更新: vector={vector_weight}, bm25={bm25_weight}")


# 全局混合检索实例
_hybrid_search: Optional[HybridSearch] = None


def get_hybrid_search(
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3,
    language: str = "chinese"
) -> HybridSearch:
    """
    获取混合检索实例（单例）

    Args:
        vector_weight: 向量检索权重
        bm25_weight: BM25 权重
        language: 语言

    Returns:
        混合检索实例
    """
    global _hybrid_search
    if _hybrid_search is None:
        _hybrid_search = HybridSearch(
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            language=language
        )
    return _hybrid_search
