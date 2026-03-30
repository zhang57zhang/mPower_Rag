"""
重排序模块
使用交叉编码器提升检索质量
"""
from typing import List, Dict, Any, Optional, Iterator
import logging
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class BaseReranker:
    """重排序器基类"""

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """
        重排序文档

        Args:
            query: 查询
            documents: 文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        raise NotImplementedError


class CrossEncoderReranker(BaseReranker):
    """基于交叉编码器的重排序器"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        初始化交叉编码器重排序器

        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载模型"""
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            logger.info(f"加载重排序模型: {self.model_name}")
        except ImportError:
            logger.warning("sentence_transformers 未安装，重排序功能不可用")
            self.model = None
        except Exception as e:
            logger.error(f"加载重排序模型失败: {e}")
            self.model = None

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """
        使用交叉编码器重排序

        Args:
            query: 查询
            documents: 文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        if self.model is None or not documents:
            return documents

        try:
            # 构建查询-文档对
            pairs = [[query, doc.page_content] for doc in documents]

            # 计算分数
            scores = self.model.predict(pairs)

            # 分配分数到元数据
            for doc, score in zip(documents, scores):
                doc.metadata["rerank_score"] = float(score)

            # 按分数排序
            documents.sort(key=lambda x: x.metadata.get("rerank_score", 0), reverse=True)

            # 截取 top_k
            if top_k is not None and top_k < len(documents):
                documents = documents[:top_k]

            logger.debug(f"重排序完成，返回 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"重排序失败: {e}")
            return documents


class KeywordReranker(BaseReranker):
    """基于关键词的重排序器（无需模型）"""

    def __init__(self, weight: float = 0.3):
        """
        初始化关键词重排序器

        Args:
            weight: 关键词权重
        """
        self.weight = weight

    def _extract_keywords(self, text: str) -> set:
        """
        提取关键词

        Args:
            text: 文本

        Returns:
            关键词集合
        """
        # 简单的分词和停用词过滤
        import jieba

        words = jieba.cut(text)
        stop_words = {"的", "是", "在", "和", "有", "我", "你", "他", "她", "它", "们"}

        keywords = {w for w in words if len(w) > 1 and w not in stop_words}

        return keywords

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """
        基于关键词重叠重排序

        Args:
            query: 查询
            documents: 文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        if not documents:
            return documents

        try:
            # 提取查询关键词
            query_keywords = self._extract_keywords(query)

            # 计算每个文档的关键词重叠度
            for doc in documents:
                doc_keywords = self._extract_keywords(doc.page_content)

                if query_keywords:
                    overlap = len(query_keywords & doc_keywords)
                    coverage = overlap / len(query_keywords)
                else:
                    coverage = 0

                # 结合原始相似度分数
                original_score = doc.metadata.get("score", 0)
                rerank_score = (original_score * (1 - self.weight)) + (coverage * self.weight)

                doc.metadata["keyword_rerank_score"] = rerank_score

            # 按重排序分数排序
            documents.sort(key=lambda x: x.metadata.get("keyword_rerank_score", 0), reverse=True)

            # 截取 top_k
            if top_k is not None and top_k < len(documents):
                documents = documents[:top_k]

            logger.debug(f"关键词重排序完成，返回 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"关键词重排序失败: {e}")
            return documents


class RerankerPipeline:
    """重排序流水线"""

    def __init__(self, rerankers: List[BaseReranker]):
        """
        初始化重排序流水线

        Args:
            rerankers: 重排序器列表
        """
        self.rerankers = rerankers

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """
        执行重排序流水线

        Args:
            query: 查询
            documents: 文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        for i, reranker in enumerate(self.rerankers):
            logger.debug(f"执行第 {i+1} 阶段重排序: {reranker.__class__.__name__}")
            documents = reranker.rerank(query, documents, top_k)

        return documents


def create_reranker(
    method: str = "cross_encoder",
    model_name: str = "BAAI/bge-reranker-base",
    **kwargs,
) -> BaseReranker:
    """
    创建重排序器

    Args:
        method: 重排序方法 (cross_encoder, keyword)
        model_name: 模型名称（仅用于 cross_encoder）
        **kwargs: 其他参数

    Returns:
        重排序器实例
    """
    if method == "cross_encoder":
        return CrossEncoderReranker(model_name=model_name)
    elif method == "keyword":
        return KeywordReranker(**kwargs)
    else:
        raise ValueError(f"未知的重排序方法: {method}")


# 全局重排序器实例
_reranker = None


def get_reranker(
    method: str = "cross_encoder",
    **kwargs,
) -> Optional[BaseReranker]:
    """获取重排序器（单例）"""
    global _reranker
    if _reranker is None:
        _reranker = create_reranker(method=method, **kwargs)
    return _reranker
