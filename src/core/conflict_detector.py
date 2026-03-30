"""
知识冲突检测器
自动检测知识库中的矛盾和冲突
"""
import re
from typing import List, Dict, Any, Tuple, Optional, Iterator
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """冲突类型"""
    FACTUAL = "factual"          # 事实冲突
    LOGICAL = "logical"          # 逻辑冲突
    TEMPORAL = "temporal"        # 时效冲突
    AUTHORITY = "authority"      # 权威冲突
    SEMANTIC = "semantic"        # 语义冲突


class ConflictSeverity(Enum):
    """冲突严重程度"""
    LOW = "low"           # 低：轻微矛盾
    MEDIUM = "medium"     # 中：明显矛盾
    HIGH = "high"         # 高：严重矛盾
    CRITICAL = "critical" # 严重：关键矛盾


@dataclass
class Conflict:
    """冲突对象"""
    id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    documents: List[Dict[str, Any]]
    description: str
    suggestion: str
    confidence: float


class KnowledgeConflictDetector:
    """知识冲突检测器"""

    def __init__(
        self,
        vector_store,
        embeddings,
        similarity_threshold: float = 0.8
    ):
        """
        初始化冲突检测器

        Args:
            vector_store: 向量存储
            embeddings: 嵌入模型
            similarity_threshold: 相似度阈值
        """
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.similarity_threshold = similarity_threshold

        # 冲突模式库
        self.conflict_patterns = self._load_conflict_patterns()

    def detect_all_conflicts(
        self,
        document_ids: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        检测所有冲突

        Args:
            document_ids: 要检查的文档ID列表（None表示全部）

        Returns:
            冲突列表
        """
        logger.info("开始检测知识冲突...")

        conflicts = []

        # 1. 检测事实冲突
        factual_conflicts = self._detect_factual_conflicts(document_ids)
        conflicts.extend(factual_conflicts)

        # 2. 检测逻辑冲突
        logical_conflicts = self._detect_logical_conflicts(document_ids)
        conflicts.extend(logical_conflicts)

        # 3. 检测时效冲突
        temporal_conflicts = self._detect_temporal_conflicts(document_ids)
        conflicts.extend(temporal_conflicts)

        # 4. 检测权威冲突
        authority_conflicts = self._detect_authority_conflicts(document_ids)
        conflicts.extend(authority_conflicts)

        # 5. 检测语义冲突
        semantic_conflicts = self._detect_semantic_conflicts(document_ids)
        conflicts.extend(semantic_conflicts)

        logger.info(f"检测完成，发现 {len(conflicts)} 个冲突")

        return conflicts

    def _detect_factual_conflicts(
        self,
        document_ids: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        检测事实冲突

        检测同一问题是否有不同的答案
        """
        conflicts = []

        # 获取所有文档
        if document_ids:
            documents = [
                self.vector_store.get_document(doc_id)
                for doc_id in document_ids
            ]
        else:
            documents = self.vector_store.get_all_documents()

        # 提取关键事实
        facts = self._extract_facts(documents)

        # 检测相似事实的矛盾
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i+1:], i+1):
                # 计算相似度
                similarity = self._calculate_similarity(
                    fact1['question'],
                    fact2['question']
                )

                # 如果问题相似但答案不同
                if similarity > self.similarity_threshold:
                    answer_similarity = self._calculate_similarity(
                        fact1['answer'],
                        fact2['answer']
                    )

                    if answer_similarity < 0.5:  # 答案差异较大
                        conflict = Conflict(
                            id=f"conflict_factual_{i}_{j}",
                            conflict_type=ConflictType.FACTUAL,
                            severity=self._assess_severity(fact1, fact2),
                            documents=[
                                {
                                    'id': fact1['doc_id'],
                                    'question': fact1['question'],
                                    'answer': fact1['answer'],
                                    'confidence': fact1.get('confidence', 0.5)
                                },
                                {
                                    'id': fact2['doc_id'],
                                    'question': fact2['question'],
                                    'answer': fact2['answer'],
                                    'confidence': fact2.get('confidence', 0.5)
                                }
                            ],
                            description=f"关于「{fact1['question']}」存在不同的答案",
                            suggestion=self._generate_factual_suggestion(fact1, fact2),
                            confidence=similarity
                        )
                        conflicts.append(conflict)

        return conflicts

    def _detect_logical_conflicts(
        self,
        document_ids: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        检测逻辑冲突

        检测知识之间是否存在逻辑矛盾
        """
        conflicts = []

        # 获取所有文档
        if document_ids:
            documents = [
                self.vector_store.get_document(doc_id)
                for doc_id in document_ids
            ]
        else:
            documents = self.vector_store.get_all_documents()

        # 检测逻辑矛盾模式
        for pattern in self.conflict_patterns['logical']:
            matches = self._find_pattern_matches(documents, pattern)

            for match in matches:
                if len(match) >= 2:
                    conflict = Conflict(
                        id=f"conflict_logical_{match[0]['doc_id']}_{match[1]['doc_id']}",
                        conflict_type=ConflictType.LOGICAL,
                        severity=ConflictSeverity.HIGH,
                        documents=[
                            {
                                'id': doc['doc_id'],
                                'content': doc['content'],
                                'pattern': pattern['name']
                            }
                            for doc in match
                        ],
                        description=f"检测到逻辑矛盾：{pattern['description']}",
                        suggestion=pattern['suggestion'],
                        confidence=0.9
                    )
                    conflicts.append(conflict)

        return conflicts

    def _detect_temporal_conflicts(
        self,
        document_ids: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        检测时效冲突

        检测新旧知识的时效性冲突
        """
        conflicts = []

        # 获取所有文档
        if document_ids:
            documents = [
                self.vector_store.get_document(doc_id)
                for doc_id in document_ids
            ]
        else:
            documents = self.vector_store.get_all_documents()

        # 按主题分组
        topic_groups = self._group_by_topic(documents)

        for topic, docs in topic_groups.items():
            if len(docs) < 2:
                continue

            # 按时间排序
            docs_sorted = sorted(
                docs,
                key=lambda x: x.get('modified_time', 0),
                reverse=True
            )

            # 检测时效冲突
            latest_doc = docs_sorted[0]
            old_docs = docs_sorted[1:]

            for old_doc in old_docs:
                # 检查内容相似度
                similarity = self._calculate_similarity(
                    latest_doc['content'],
                    old_doc['content']
                )

                # 如果主题相同但内容差异大
                if similarity > 0.7 and similarity < 0.95:
                    conflict = Conflict(
                        id=f"conflict_temporal_{latest_doc['id']}_{old_doc['id']}",
                        conflict_type=ConflictType.TEMPORAL,
                        severity=ConflictSeverity.MEDIUM,
                        documents=[
                            {
                                'id': latest_doc['id'],
                                'content': latest_doc['content'],
                                'timestamp': latest_doc.get('modified_time'),
                                'status': '最新'
                            },
                            {
                                'id': old_doc['id'],
                                'content': old_doc['content'],
                                'timestamp': old_doc.get('modified_time'),
                                'status': '旧版本'
                            }
                        ],
                        description=f"关于「{topic}」存在新旧版本冲突",
                        suggestion="建议使用最新版本的文档，或合并两个版本的信息",
                        confidence=0.85
                    )
                    conflicts.append(conflict)

        return conflicts

    def _detect_authority_conflicts(
        self,
        document_ids: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        检测权威冲突

        检测不同权威来源的冲突
        """
        conflicts = []

        # 获取所有文档
        if document_ids:
            documents = [
                self.vector_store.get_document(doc_id)
                for doc_id in document_ids
            ]
        else:
            documents = self.vector_store.get_all_documents()

        # 按主题分组
        topic_groups = self._group_by_topic(documents)

        for topic, docs in topic_groups.items():
            if len(docs) < 2:
                continue

            # 检测权威来源的差异
            authority_levels = defaultdict(list)
            for doc in docs:
                authority = doc.get('metadata', {}).get('authority', 'unknown')
                authority_levels[authority].append(doc)

            # 如果不同权威来源有冲突
            if len(authority_levels) > 1:
                # 检查内容差异
                all_contents = [doc['content'] for doc in docs]
                similarities = []

                for i, content1 in enumerate(all_contents):
                    for j, content2 in enumerate(all_contents[i+1:], i+1):
                        sim = self._calculate_similarity(content1, content2)
                        similarities.append(sim)

                avg_similarity = sum(similarities) / len(similarities) if similarities else 1.0

                if avg_similarity < 0.7:  # 存在明显差异
                    conflict = Conflict(
                        id=f"conflict_authority_{topic}",
                        conflict_type=ConflictType.AUTHORITY,
                        severity=ConflictSeverity.MEDIUM,
                        documents=[
                            {
                                'id': doc['id'],
                                'content': doc['content'][:200],
                                'authority': doc.get('metadata', {}).get('authority', 'unknown')
                            }
                            for doc in docs
                        ],
                        description=f"关于「{topic}」不同权威来源存在差异",
                        suggestion="建议优先采用权威性更高的来源，或咨询专家进行裁决",
                        confidence=0.75
                    )
                    conflicts.append(conflict)

        return conflicts

    def _detect_semantic_conflicts(
        self,
        document_ids: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        检测语义冲突

        检测语义层面的矛盾
        """
        conflicts = []

        # 获取所有文档
        if document_ids:
            documents = [
                self.vector_store.get_document(doc_id)
                for doc_id in document_ids
            ]
        else:
            documents = self.vector_store.get_all_documents()

        # 检测否定词冲突
        negation_patterns = [
            r'不(能|会|应该|需要)',
            r'禁止',
            r'不允许',
            r'切勿',
            r'不要',
        ]

        for i, doc1 in enumerate(documents):
            for j, doc2 in enumerate(documents[i+1:], i+1):
                # 检查语义相似度
                similarity = self._calculate_similarity(
                    doc1['content'],
                    doc2['content']
                )

                if similarity > 0.7:
                    # 检查是否存在否定冲突
                    has_negation1 = any(
                        re.search(pattern, doc1['content'])
                        for pattern in negation_patterns
                    )
                    has_negation2 = any(
                        re.search(pattern, doc2['content'])
                        for pattern in negation_patterns
                    )

                    # 如果一个肯定一个否定
                    if has_negation1 != has_negation2:
                        conflict = Conflict(
                            id=f"conflict_semantic_{doc1['id']}_{doc2['id']}",
                            conflict_type=ConflictType.SEMANTIC,
                            severity=ConflictSeverity.HIGH,
                            documents=[
                                {
                                    'id': doc1['id'],
                                    'content': doc1['content'][:200],
                                    'has_negation': has_negation1
                                },
                                {
                                    'id': doc2['id'],
                                    'content': doc2['content'][:200],
                                    'has_negation': has_negation2
                                }
                            ],
                            description="检测到语义层面的矛盾（肯定 vs 否定）",
                            suggestion="建议检查两个文档的上下文，确定正确的表述",
                            confidence=0.8
                        )
                        conflicts.append(conflict)

        return conflicts

    # ==================== 辅助方法 ====================

    def _load_conflict_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载冲突模式库"""
        return {
            'logical': [
                {
                    'name': 'require_prohibit',
                    'pattern': r'(需要|必须|应该).*?(禁止|不允许|不能)',
                    'description': '同时要求做某事和禁止做某事',
                    'suggestion': '检查文档中的要求和禁止是否矛盾'
                },
                {
                    'name': 'enable_disable',
                    'pattern': r'(启用|开启|激活).*?(禁用|关闭|停用)',
                    'description': '同时启用和禁用同一功能',
                    'suggestion': '确认功能的正确状态'
                }
            ]
        }

    def _extract_facts(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从文档中提取事实"""
        facts = []

        for doc in documents:
            content = doc.get('content', '')

            # 简单的事实提取（实际可以使用更复杂的 NLP）
            # 提取问答对
            qa_pattern = r'问[：:](.*?)\s*答[：:](.*?)(?=问[：:]|$)'
            matches = re.findall(qa_pattern, content, re.DOTALL)

            for question, answer in matches:
                facts.append({
                    'doc_id': doc['id'],
                    'question': question.strip(),
                    'answer': answer.strip(),
                    'confidence': doc.get('metadata', {}).get('confidence', 0.5)
                })

        return facts

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 使用嵌入模型计算相似度
        try:
            emb1 = self.embeddings.embed_query(text1)
            emb2 = self.embeddings.embed_query(text2)

            # 余弦相似度
            import numpy as np
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

            return float(similarity)
        except Exception as e:
            logger.warning(f"相似度计算失败: {e}")
            return 0.0

    def _assess_severity(self, fact1: Dict, fact2: Dict) -> ConflictSeverity:
        """评估冲突严重程度"""
        # 基于置信度差异评估
        conf_diff = abs(
            fact1.get('confidence', 0.5) - fact2.get('confidence', 0.5)
        )

        if conf_diff < 0.2:
            return ConflictSeverity.HIGH
        elif conf_diff < 0.5:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW

    def _generate_factual_suggestion(
        self,
        fact1: Dict,
        fact2: Dict
    ) -> str:
        """生成事实冲突的解决建议"""
        conf1 = fact1.get('confidence', 0.5)
        conf2 = fact2.get('confidence', 0.5)

        if conf1 > conf2:
            return f"建议采用第一个答案（置信度 {conf1:.2f} > {conf2:.2f}）"
        elif conf2 > conf1:
            return f"建议采用第二个答案（置信度 {conf2:.2f} > {conf1:.2f}）"
        else:
            return "两个答案置信度相同，建议咨询专家进行裁决"

    def _find_pattern_matches(
        self,
        documents: List[Dict[str, Any]],
        pattern: Dict[str, Any]
    ) -> List[List[Dict[str, Any]]]:
        """查找匹配模式的文档组合"""
        matches = []

        regex = re.compile(pattern['pattern'], re.DOTALL)

        matched_docs = []
        for doc in documents:
            if regex.search(doc.get('content', '')):
                matched_docs.append(doc)

        # 如果找到多个匹配的文档，返回它们
        if len(matched_docs) >= 2:
            matches.append(matched_docs)

        return matches

    def _group_by_topic(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """按主题分组文档"""
        topic_groups = defaultdict(list)

        for doc in documents:
            # 简单的主题提取（可以使用更复杂的 NLP）
            topic = doc.get('metadata', {}).get('topic', 'general')
            topic_groups[topic].append(doc)

        return topic_groups


def get_conflict_detector(
    vector_store,
    embeddings,
    similarity_threshold: float = 0.8
) -> KnowledgeConflictDetector:
    """
    获取冲突检测器实例

    Args:
        vector_store: 向量存储
        embeddings: 嵌入模型
        similarity_threshold: 相似度阈值

    Returns:
        冲突检测器实例
    """
    return KnowledgeConflictDetector(vector_store, embeddings, similarity_threshold)
