"""
去重管理器
确保知识文档的"不重"
"""
import hashlib
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class DocumentFingerprint:
    """文档指纹"""
    doc_id: str
    content_hash: str          # 内容哈希
    semantic_hash: str         # 语义哈希（基于嵌入）
    minhash_signature: List[int] = field(default_factory=list)  # MinHash 签名
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content_hash": self.content_hash,
            "semantic_hash": self.semantic_hash,
            "minhash_signature": self.minhash_signature,
            "created_at": self.created_at,
            "source": self.source,
        }


@dataclass
class DuplicateResult:
    """去重检查结果"""
    is_duplicate: bool
    duplicate_type: str        # exact, near, semantic
    duplicate_of: Optional[str] = None
    similarity: float = 0.0
    action: str = "keep"       # keep, skip, merge


class DeduplicationManager:
    """
    去重管理器
    
    支持三层去重：
    1. 精确去重 - 内容哈希完全匹配
    2. 近似去重 - MinHash/Jaccard 相似度
    3. 语义去重 - 向量嵌入相似度
    """
    
    def __init__(
        self,
        exact_threshold: float = 1.0,     # 精确匹配阈值
        near_threshold: float = 0.9,       # 近似匹配阈值
        semantic_threshold: float = 0.95,  # 语义匹配阈值
        use_minhash: bool = True,
        num_hashes: int = 128,             # MinHash 哈希数
    ):
        """
        初始化去重管理器
        
        Args:
            exact_threshold: 精确匹配阈值
            near_threshold: 近似匹配阈值
            semantic_threshold: 语义匹配阈值
            use_minhash: 是否使用 MinHash
            num_hashes: MinHash 哈希数量
        """
        self.exact_threshold = exact_threshold
        self.near_threshold = near_threshold
        self.semantic_threshold = semantic_threshold
        self.use_minhash = use_minhash
        self.num_hashes = num_hashes
        
        # 指纹索引
        self._fingerprints: Dict[str, DocumentFingerprint] = {}
        self._content_hash_index: Dict[str, str] = {}  # content_hash -> doc_id
        self._minhash_index: Dict[int, Set[str]] = {}  # bucket -> doc_ids
        
        logger.info(f"DeduplicationManager initialized (thresholds: exact={exact_threshold}, near={near_threshold}, semantic={semantic_threshold})")
    
    def check_duplicate(
        self,
        content: str,
        doc_id: Optional[str] = None,
        embedding: Optional[List[float]] = None,
    ) -> DuplicateResult:
        """
        检查是否重复
        
        Args:
            content: 文档内容
            doc_id: 文档 ID（可选，用于更新）
            embedding: 文档嵌入向量（可选，用于语义去重）
            
        Returns:
            去重检查结果
        """
        # 1. 精确匹配检查
        content_hash = self._compute_content_hash(content)
        
        if content_hash in self._content_hash_index:
            existing_id = self._content_hash_index[content_hash]
            if existing_id != doc_id:
                return DuplicateResult(
                    is_duplicate=True,
                    duplicate_type="exact",
                    duplicate_of=existing_id,
                    similarity=1.0,
                    action="skip",
                )
        
        # 2. 近似匹配检查（MinHash）
        if self.use_minhash:
            minhash = self._compute_minhash(content)
            similar_docs = self._find_similar_by_minhash(minhash)
            
            for similar_id, similarity in similar_docs:
                if similar_id != doc_id and similarity >= self.near_threshold:
                    return DuplicateResult(
                        is_duplicate=True,
                        duplicate_type="near",
                        duplicate_of=similar_id,
                        similarity=similarity,
                        action="skip",
                    )
        
        # 3. 语义匹配检查（如果有嵌入）
        if embedding is not None:
            similar_doc = self._find_similar_by_embedding(embedding)
            if similar_doc and similar_doc[1] >= self.semantic_threshold:
                return DuplicateResult(
                    is_duplicate=True,
                    duplicate_type="semantic",
                    duplicate_of=similar_doc[0],
                    similarity=similar_doc[1],
                    action="merge",  # 语义相似可考虑合并
                )
        
        return DuplicateResult(
            is_duplicate=False,
            duplicate_type="none",
            action="keep",
        )
    
    def register_document(
        self,
        doc_id: str,
        content: str,
        source: str = "",
        embedding: Optional[List[float]] = None,
    ) -> DocumentFingerprint:
        """
        注册文档到去重索引
        
        Args:
            doc_id: 文档 ID
            content: 文档内容
            source: 来源
            embedding: 嵌入向量
            
        Returns:
            文档指纹
        """
        # 计算哈希
        content_hash = self._compute_content_hash(content)
        semantic_hash = self._compute_semantic_hash(embedding) if embedding else ""
        minhash = self._compute_minhash(content) if self.use_minhash else []
        
        # 创建指纹
        fingerprint = DocumentFingerprint(
            doc_id=doc_id,
            content_hash=content_hash,
            semantic_hash=semantic_hash,
            minhash_signature=minhash,
            source=source,
        )
        
        # 更新索引
        self._fingerprints[doc_id] = fingerprint
        self._content_hash_index[content_hash] = doc_id
        
        # 更新 MinHash 索引
        if self.use_minhash and minhash:
            self._update_minhash_index(doc_id, minhash)
        
        logger.debug(f"Registered document: {doc_id}")
        
        return fingerprint
    
    def remove_document(self, doc_id: str) -> bool:
        """
        从索引中移除文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            是否成功移除
        """
        if doc_id not in self._fingerprints:
            return False
        
        fingerprint = self._fingerprints[doc_id]
        
        # 移除内容哈希索引
        if fingerprint.content_hash in self._content_hash_index:
            del self._content_hash_index[fingerprint.content_hash]
        
        # 移除 MinHash 索引
        if self.use_minhash:
            self._remove_from_minhash_index(doc_id, fingerprint.minhash_signature)
        
        # 移除指纹
        del self._fingerprints[doc_id]
        
        logger.debug(f"Removed document: {doc_id}")
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_documents": len(self._fingerprints),
            "unique_content_hashes": len(self._content_hash_index),
            "minhash_buckets": len(self._minhash_index),
        }
    
    def clear(self):
        """清空索引"""
        self._fingerprints.clear()
        self._content_hash_index.clear()
        self._minhash_index.clear()
        logger.info("Deduplication index cleared")
    
    def _compute_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        # 标准化内容
        normalized = " ".join(content.split()).lower()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _compute_semantic_hash(self, embedding: Optional[List[float]]) -> str:
        """计算语义哈希"""
        if embedding is None:
            return ""
        
        # 将嵌入向量转换为哈希
        # 简单实现：使用前几个维度的符号
        bits = []
        for i, val in enumerate(embedding[:64]):
            bits.append('1' if val > 0 else '0')
        
        binary = ''.join(bits)
        return hashlib.md5(binary.encode()).hexdigest()
    
    def _compute_minhash(self, content: str) -> List[int]:
        """
        计算 MinHash 签名
        
        使用字符 n-gram 作为特征
        """
        # 生成 n-gram
        n = 3
        content = content.lower()
        ngrams = set()
        
        for i in range(len(content) - n + 1):
            ngrams.add(content[i:i+n])
        
        if not ngrams:
            return []
        
        # 计算 MinHash
        minhash = []
        for i in range(self.num_hashes):
            min_val = float('inf')
            for ngram in ngrams:
                # 使用不同的哈希种子
                h = hash(f"{i}:{ngram}")
                min_val = min(min_val, h)
            minhash.append(min_val)
        
        return minhash
    
    def _update_minhash_index(self, doc_id: str, minhash: List[int]):
        """更新 MinHash 索引（LSH）"""
        # 使用 LSH 分桶
        num_bands = 16
        rows_per_band = self.num_hashes // num_bands
        
        for band in range(num_bands):
            start = band * rows_per_band
            end = start + rows_per_band
            bucket = hash(tuple(minhash[start:end]))
            
            if bucket not in self._minhash_index:
                self._minhash_index[bucket] = set()
            self._minhash_index[bucket].add(doc_id)
    
    def _remove_from_minhash_index(self, doc_id: str, minhash: List[int]):
        """从 MinHash 索引中移除"""
        num_bands = 16
        rows_per_band = self.num_hashes // num_bands
        
        for band in range(num_bands):
            start = band * rows_per_band
            end = start + rows_per_band
            bucket = hash(tuple(minhash[start:end]))
            
            if bucket in self._minhash_index:
                self._minhash_index[bucket].discard(doc_id)
    
    def _find_similar_by_minhash(self, minhash: List[int]) -> List[Tuple[str, float]]:
        """使用 MinHash 查找相似文档"""
        if not minhash:
            return []
        
        # 查找候选
        candidates = set()
        num_bands = 16
        rows_per_band = len(minhash) // num_bands
        
        for band in range(num_bands):
            start = band * rows_per_band
            end = start + rows_per_band
            bucket = hash(tuple(minhash[start:end]))
            
            if bucket in self._minhash_index:
                candidates.update(self._minhash_index[bucket])
        
        # 计算精确 Jaccard 相似度
        results = []
        for doc_id in candidates:
            if doc_id in self._fingerprints:
                other_minhash = self._fingerprints[doc_id].minhash_signature
                if other_minhash:
                    similarity = self._jaccard_similarity(minhash, other_minhash)
                    results.append((doc_id, similarity))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:10]  # 返回前 10 个
    
    def _jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """计算 Jaccard 相似度（基于 MinHash）"""
        if len(sig1) != len(sig2) or len(sig1) == 0:
            return 0.0
        
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)
    
    def _find_similar_by_embedding(
        self,
        embedding: List[float],
    ) -> Optional[Tuple[str, float]]:
        """使用嵌入查找相似文档"""
        best_match = None
        best_similarity = 0.0
        
        for doc_id, fingerprint in self._fingerprints.items():
            if fingerprint.semantic_hash:
                # 简化：只比较语义哈希
                # 实际应计算余弦相似度
                pass
        
        # 如果没有存储嵌入，返回 None
        # 实际实现需要向量数据库支持
        return best_match
    
    def batch_deduplicate(
        self,
        documents: List[Tuple[str, str]],  # (doc_id, content)
    ) -> Tuple[List[str], List[str]]:
        """
        批量去重
        
        Args:
            documents: 文档列表 (doc_id, content)
            
        Returns:
            (保留的ID列表, 重复的ID列表)
        """
        kept = []
        duplicates = []
        
        for doc_id, content in documents:
            result = self.check_duplicate(content, doc_id)
            
            if result.is_duplicate:
                duplicates.append(doc_id)
                logger.info(f"Duplicate found: {doc_id} (similar to {result.duplicate_of}, type={result.duplicate_type})")
            else:
                self.register_document(doc_id, content)
                kept.append(doc_id)
        
        logger.info(f"Batch deduplication: {len(kept)} kept, {len(duplicates)} duplicates")
        
        return kept, duplicates
