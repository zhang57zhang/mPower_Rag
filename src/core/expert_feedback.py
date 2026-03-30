"""
专家反馈系统
支持专家对知识进行评分、修正和审核
"""
import json
import time
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """反馈类型"""
    RATING = "rating"              # 评分
    CORRECTION = "correction"      # 修正
    APPROVAL = "approval"          # 批准
    REJECTION = "rejection"        # 拒绝
    SUGGESTION = "suggestion"      # 建议


class ReviewStatus(Enum):
    """审核状态"""
    PENDING = "pending"            # 待审核
    APPROVED = "approved"          # 已批准
    REJECTED = "rejected"          # 已拒绝
    IMPLEMENTED = "implemented"    # 已实施


@dataclass
class Feedback:
    """反馈对象"""
    id: str
    feedback_type: FeedbackType
    query_id: str
    answer_id: str
    expert_id: str
    rating: Optional[int] = None  # 1-5 星
    correction: Optional[str] = None
    reason: Optional[str] = None
    timestamp: str = ""
    review_status: ReviewStatus = ReviewStatus.PENDING
    reviewer_id: Optional[str] = None
    review_comment: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class KnowledgeVersion:
    """知识版本对象"""
    id: str
    knowledge_id: str
    version_number: int
    content: str
    metadata: Dict[str, Any]
    created_by: str
    created_at: str
    change_reason: str
    parent_version: Optional[str] = None


class ExpertFeedbackSystem:
    """专家反馈系统"""

    def __init__(
        self,
        feedback_storage_path: str = "./data/feedback",
        knowledge_storage_path: str = "./data/knowledge_versions"
    ):
        """
        初始化专家反馈系统

        Args:
            feedback_storage_path: 反馈存储路径
            knowledge_storage_path: 知识版本存储路径
        """
        self.feedback_storage_path = Path(feedback_storage_path)
        self.knowledge_storage_path = Path(knowledge_storage_path)

        # 创建存储目录
        self.feedback_storage_path.mkdir(parents=True, exist_ok=True)
        self.knowledge_storage_path.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self.feedback_cache: Dict[str, Feedback] = {}
        self.version_cache: Dict[str, List[KnowledgeVersion]] = {}

        # 加载已有数据
        self._load_feedbacks()
        self._load_versions()

    def submit_feedback(
        self,
        feedback_type: FeedbackType,
        query_id: str,
        answer_id: str,
        expert_id: str,
        rating: Optional[int] = None,
        correction: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Feedback:
        """
        提交反馈

        Args:
            feedback_type: 反馈类型
            query_id: 查询 ID
            answer_id: 答案 ID
            expert_id: 专家 ID
            rating: 评分（1-5）
            correction: 修正内容
            reason: 原因说明

        Returns:
            反馈对象
        """
        # 生成反馈 ID
        feedback_id = f"feedback_{int(time.time() * 1000)}"

        # 创建反馈对象
        feedback = Feedback(
            id=feedback_id,
            feedback_type=feedback_type,
            query_id=query_id,
            answer_id=answer_id,
            expert_id=expert_id,
            rating=rating,
            correction=correction,
            reason=reason
        )

        # 保存到缓存
        self.feedback_cache[feedback_id] = feedback

        # 持久化存储
        self._save_feedback(feedback)

        logger.info(f"反馈已提交: {feedback_id} by {expert_id}")

        return feedback

    def review_feedback(
        self,
        feedback_id: str,
        reviewer_id: str,
        approved: bool,
        comment: Optional[str] = None
    ) -> Optional[Feedback]:
        """
        审核反馈

        Args:
            feedback_id: 反馈 ID
            reviewer_id: 审核者 ID
            approved: 是否批准
            comment: 审核意见

        Returns:
            更新后的反馈对象
        """
        feedback = self.feedback_cache.get(feedback_id)

        if not feedback:
            logger.error(f"反馈不存在: {feedback_id}")
            return None

        # 更新审核状态
        feedback.review_status = ReviewStatus.APPROVED if approved else ReviewStatus.REJECTED
        feedback.reviewer_id = reviewer_id
        feedback.review_comment = comment

        # 保存更新
        self._save_feedback(feedback)

        logger.info(f"反馈已审核: {feedback_id}, 状态: {feedback.review_status.value}")

        return feedback

    def implement_feedback(
        self,
        feedback_id: str,
        vector_store
    ) -> bool:
        """
        实施反馈（更新知识库）

        Args:
            feedback_id: 反馈 ID
            vector_store: 向量存储

        Returns:
            是否成功
        """
        feedback = self.feedback_cache.get(feedback_id)

        if not feedback:
            logger.error(f"反馈不存在: {feedback_id}")
            return False

        if feedback.review_status != ReviewStatus.APPROVED:
            logger.error(f"反馈未批准，无法实施: {feedback_id}")
            return False

        if feedback.feedback_type != FeedbackType.CORRECTION:
            logger.error(f"只有修正类型的反馈可以实施: {feedback_id}")
            return False

        try:
            # 获取原始知识
            knowledge_id = feedback.answer_id
            old_knowledge = vector_store.get_document(knowledge_id)

            if not old_knowledge:
                logger.error(f"知识不存在: {knowledge_id}")
                return False

            # 创建新版本
            new_version = self._create_knowledge_version(
                knowledge_id=knowledge_id,
                new_content=feedback.correction,
                created_by=feedback.expert_id,
                change_reason=feedback.reason or "专家修正"
            )

            # 更新向量存储
            vector_store.update_document(
                knowledge_id,
                content=feedback.correction,
                metadata={
                    **old_knowledge.get('metadata', {}),
                    'version': new_version.version_number,
                    'last_modified_by': feedback.expert_id,
                    'modification_reason': feedback.reason
                }
            )

            # 更新反馈状态
            feedback.review_status = ReviewStatus.IMPLEMENTED
            self._save_feedback(feedback)

            logger.info(f"反馈已实施: {feedback_id}")

            return True

        except Exception as e:
            logger.error(f"实施反馈失败: {e}")
            return False

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        获取反馈统计

        Returns:
            统计数据
        """
        total_feedbacks = len(self.feedback_cache)

        by_type = {}
        by_status = {}
        avg_rating = 0.0
        rating_count = 0

        for feedback in self.feedback_cache.values():
            # 按类型统计
            type_key = feedback.feedback_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # 按状态统计
            status_key = feedback.review_status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            # 评分统计
            if feedback.rating:
                avg_rating += feedback.rating
                rating_count += 1

        if rating_count > 0:
            avg_rating = round(avg_rating / rating_count, 2)

        return {
            'total_feedbacks': total_feedbacks,
            'by_type': by_type,
            'by_status': by_status,
            'average_rating': avg_rating,
            'pending_reviews': by_status.get('pending', 0)
        }

    def get_pending_reviews(self) -> List[Feedback]:
        """
        获取待审核的反馈

        Returns:
            待审核反馈列表
        """
        return [
            feedback
            for feedback in self.feedback_cache.values()
            if feedback.review_status == ReviewStatus.PENDING
        ]

    def get_feedback_by_query(self, query_id: str) -> List[Feedback]:
        """
        获取查询相关的所有反馈

        Args:
            query_id: 查询 ID

        Returns:
            反馈列表
        """
        return [
            feedback
            for feedback in self.feedback_cache.values()
            if feedback.query_id == query_id
        ]

    def get_knowledge_versions(
        self,
        knowledge_id: str
    ) -> List[KnowledgeVersion]:
        """
        获取知识的所有版本

        Args:
            knowledge_id: 知识 ID

        Returns:
            版本列表
        """
        return self.version_cache.get(knowledge_id, [])

    def rollback_knowledge(
        self,
        knowledge_id: str,
        version_number: int,
        vector_store
    ) -> bool:
        """
        回滚知识到指定版本

        Args:
            knowledge_id: 知识 ID
            version_number: 版本号
            vector_store: 向量存储

        Returns:
            是否成功
        """
        versions = self.version_cache.get(knowledge_id, [])

        target_version = None
        for version in versions:
            if version.version_number == version_number:
                target_version = version
                break

        if not target_version:
            logger.error(f"版本不存在: {knowledge_id} v{version_number}")
            return False

        try:
            # 获取当前知识
            current_knowledge = vector_store.get_document(knowledge_id)

            # 创建回滚版本
            rollback_version = self._create_knowledge_version(
                knowledge_id=knowledge_id,
                new_content=target_version.content,
                created_by="system",
                change_reason=f"回滚到版本 {version_number}"
            )

            # 更新向量存储
            vector_store.update_document(
                knowledge_id,
                content=target_version.content,
                metadata={
                    **current_knowledge.get('metadata', {}),
                    'version': rollback_version.version_number,
                    'rollback_from': current_knowledge.get('metadata', {}).get('version'),
                    'rollback_reason': f"回滚到版本 {version_number}"
                }
            )

            logger.info(f"知识已回滚: {knowledge_id} -> v{version_number}")

            return True

        except Exception as e:
            logger.error(f"回滚失败: {e}")
            return False

    # ==================== 私有方法 ====================

    def _create_knowledge_version(
        self,
        knowledge_id: str,
        new_content: str,
        created_by: str,
        change_reason: str
    ) -> KnowledgeVersion:
        """
        创建知识版本

        Args:
            knowledge_id: 知识 ID
            new_content: 新内容
            created_by: 创建者
            change_reason: 变更原因

        Returns:
            版本对象
        """
        # 获取当前版本号
        versions = self.version_cache.get(knowledge_id, [])
        version_number = len(versions) + 1

        # 创建版本对象
        version = KnowledgeVersion(
            id=f"version_{knowledge_id}_{version_number}",
            knowledge_id=knowledge_id,
            version_number=version_number,
            content=new_content,
            metadata={
                'created_by': created_by,
                'change_reason': change_reason
            },
            created_by=created_by,
            created_at=datetime.utcnow().isoformat(),
            change_reason=change_reason,
            parent_version=versions[-1].id if versions else None
        )

        # 添加到缓存
        if knowledge_id not in self.version_cache:
            self.version_cache[knowledge_id] = []
        self.version_cache[knowledge_id].append(version)

        # 持久化存储
        self._save_version(version)

        return version

    def _save_feedback(self, feedback: Feedback):
        """保存反馈到文件"""
        file_path = self.feedback_storage_path / f"{feedback.id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(feedback), f, ensure_ascii=False, indent=2)

    def _save_version(self, version: KnowledgeVersion):
        """保存版本到文件"""
        file_path = self.knowledge_storage_path / f"{version.id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(version), f, ensure_ascii=False, indent=2)

    def _load_feedbacks(self):
        """加载所有反馈"""
        for file_path in self.feedback_storage_path.glob("feedback_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    feedback = Feedback(**data)
                    self.feedback_cache[feedback.id] = feedback
            except Exception as e:
                logger.error(f"加载反馈失败 {file_path}: {e}")

        logger.info(f"已加载 {len(self.feedback_cache)} 个反馈")

    def _load_versions(self):
        """加载所有版本"""
        for file_path in self.knowledge_storage_path.glob("version_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = KnowledgeVersion(**data)

                    if version.knowledge_id not in self.version_cache:
                        self.version_cache[version.knowledge_id] = []
                    self.version_cache[version.knowledge_id].append(version)
            except Exception as e:
                logger.error(f"加载版本失败 {file_path}: {e}")

        # 按版本号排序
        for knowledge_id in self.version_cache:
            self.version_cache[knowledge_id].sort(
                key=lambda v: v.version_number
            )

        logger.info(f"已加载 {sum(len(v) for v in self.version_cache.values())} 个版本")


def get_expert_feedback_system(
    feedback_storage_path: str = "./data/feedback",
    knowledge_storage_path: str = "./data/knowledge_versions"
) -> ExpertFeedbackSystem:
    """
    获取专家反馈系统实例

    Args:
        feedback_storage_path: 反馈存储路径
        knowledge_storage_path: 知识版本存储路径

    Returns:
        专家反馈系统实例
    """
    return ExpertFeedbackSystem(feedback_storage_path, knowledge_storage_path)
