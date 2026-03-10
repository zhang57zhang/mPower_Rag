"""
专家接口 API
提供专家反馈、审核、评分等接口
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Expert Interface"])


# ==================== 请求模型 ====================

class FeedbackSubmission(BaseModel):
    """反馈提交"""
    query_id: str = Field(..., description="查询 ID")
    answer_id: str = Field(..., description="答案 ID")
    feedback_type: str = Field(..., description="反馈类型：rating, correction, approval, rejection, suggestion")
    expert_id: str = Field(..., description="专家 ID")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分（1-5星）")
    correction: Optional[str] = Field(None, description="修正内容")
    reason: Optional[str] = Field(None, description="原因说明")


class FeedbackReview(BaseModel):
    """反馈审核"""
    reviewer_id: str = Field(..., description="审核者 ID")
    approved: bool = Field(..., description="是否批准")
    comment: Optional[str] = Field(None, description="审核意见")


# ==================== 响应模型 ====================

class FeedbackResponse(BaseModel):
    """反馈响应"""
    status: str
    feedback_id: str
    review_status: str
    message: str


class FeedbackStatsResponse(BaseModel):
    """反馈统计响应"""
    total_feedbacks: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    average_rating: float
    pending_reviews: int


# ==================== API 接口 ====================

@router.post("/feedback/submit", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackSubmission):
    """
    提交专家反馈

    支持多种反馈类型：
    - rating: 评分（1-5星）
    - correction: 修正答案
    - approval: 批准答案
    - rejection: 拒绝答案
    - suggestion: 改进建议

    Args:
        request: 反馈提交请求

    Returns:
        反馈提交结果
    """
    try:
        from core.expert_feedback import get_expert_feedback_system, FeedbackType

        # 初始化反馈系统
        feedback_system = get_expert_feedback_system()

        # 验证反馈类型
        try:
            feedback_type = FeedbackType(request.feedback_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的反馈类型: {request.feedback_type}"
            )

        # 验证必填字段
        if feedback_type == FeedbackType.RATING and not request.rating:
            raise HTTPException(
                status_code=400,
                detail="评分反馈必须提供 rating 字段"
            )

        if feedback_type == FeedbackType.CORRECTION and not request.correction:
            raise HTTPException(
                status_code=400,
                detail="修正反馈必须提供 correction 字段"
            )

        # 提交反馈
        feedback = feedback_system.submit_feedback(
            feedback_type=feedback_type,
            query_id=request.query_id,
            answer_id=request.answer_id,
            expert_id=request.expert_id,
            rating=request.rating,
            correction=request.correction,
            reason=request.reason
        )

        return FeedbackResponse(
            status="submitted",
            feedback_id=feedback.id,
            review_status=feedback.review_status.value,
            message="反馈已提交，等待审核"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats():
    """
    获取反馈统计

    Returns:
        反馈统计数据
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()
        stats = feedback_system.get_feedback_statistics()

        return FeedbackStatsResponse(**stats)

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/pending")
async def get_pending_reviews():
    """
    获取待审核的反馈列表

    Returns:
        待审核反馈列表
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()
        pending = feedback_system.get_pending_reviews()

        return {
            'pending_count': len(pending),
            'feedbacks': [
                {
                    'id': f.id,
                    'type': f.feedback_type.value,
                    'query_id': f.query_id,
                    'answer_id': f.answer_id,
                    'expert_id': f.expert_id,
                    'rating': f.rating,
                    'correction': f.correction,
                    'reason': f.reason,
                    'timestamp': f.timestamp
                }
                for f in pending
            ]
        }

    except Exception as e:
        logger.error(f"获取待审核反馈失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{feedback_id}/review")
async def review_feedback(
    feedback_id: str,
    request: FeedbackReview
):
    """
    审核反馈

    只有管理员或资深专家可以审核反馈

    Args:
        feedback_id: 反馈 ID
        request: 审核请求

    Returns:
        审核结果
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()

        # 审核反馈
        feedback = feedback_system.review_feedback(
            feedback_id=feedback_id,
            reviewer_id=request.reviewer_id,
            approved=request.approved,
            comment=request.comment
        )

        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")

        return {
            'status': 'reviewed',
            'feedback_id': feedback.id,
            'review_status': feedback.review_status.value,
            'reviewer_id': feedback.reviewer_id,
            'message': '反馈已审核'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"审核反馈失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{feedback_id}/implement")
async def implement_feedback(feedback_id: str):
    """
    实施反馈

    将批准的修正应用到知识库

    Args:
        feedback_id: 反馈 ID

    Returns:
        实施结果
    """
    try:
        from core.expert_feedback import get_expert_feedback_system
        from core.vector_store import get_vector_store

        feedback_system = get_expert_feedback_system()
        vector_store = get_vector_store()

        # 实施反馈
        success = feedback_system.implement_feedback(
            feedback_id=feedback_id,
            vector_store=vector_store
        )

        if success:
            return {
                'status': 'implemented',
                'feedback_id': feedback_id,
                'message': '反馈已实施，知识库已更新'
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="实施失败，请检查反馈状态或权限"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"实施反馈失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/query/{query_id}")
async def get_feedback_by_query(query_id: str):
    """
    获取查询相关的所有反馈

    Args:
        query_id: 查询 ID

    Returns:
        反馈列表
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()
        feedbacks = feedback_system.get_feedback_by_query(query_id)

        return {
            'query_id': query_id,
            'feedback_count': len(feedbacks),
            'feedbacks': [
                {
                    'id': f.id,
                    'type': f.feedback_type.value,
                    'expert_id': f.expert_id,
                    'rating': f.rating,
                    'review_status': f.review_status.value,
                    'timestamp': f.timestamp
                }
                for f in feedbacks
            ]
        }

    except Exception as e:
        logger.error(f"获取反馈失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{knowledge_id}/versions")
async def get_knowledge_versions(knowledge_id: str):
    """
    获取知识的所有版本历史

    Args:
        knowledge_id: 知识 ID

    Returns:
        版本历史列表
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()
        versions = feedback_system.get_knowledge_versions(knowledge_id)

        return {
            'knowledge_id': knowledge_id,
            'version_count': len(versions),
            'versions': [
                {
                    'version_number': v.version_number,
                    'created_at': v.created_at,
                    'created_by': v.created_by,
                    'change_reason': v.change_reason,
                    'content_preview': v.content[:200] + '...' if len(v.content) > 200 else v.content,
                    'metadata': v.metadata
                }
                for v in versions
            ]
        }

    except Exception as e:
        logger.error(f"获取版本历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/{knowledge_id}/rollback/{version_number}")
async def rollback_knowledge_version(
    knowledge_id: str,
    version_number: int
):
    """
    回滚知识到指定版本

    Args:
        knowledge_id: 知识 ID
        version_number: 目标版本号

    Returns:
        回滚结果
    """
    try:
        from core.expert_feedback import get_expert_feedback_system
        from core.vector_store import get_vector_store

        feedback_system = get_expert_feedback_system()
        vector_store = get_vector_store()

        # 执行回滚
        success = feedback_system.rollback_knowledge(
            knowledge_id=knowledge_id,
            version_number=version_number,
            vector_store=vector_store
        )

        if success:
            return {
                'status': 'success',
                'knowledge_id': knowledge_id,
                'rolled_back_to': version_number,
                'message': f'已成功回滚到版本 {version_number}'
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="回滚失败，请检查版本号是否正确"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回滚失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experts/{expert_id}/contributions")
async def get_expert_contributions(expert_id: str):
    """
    获取专家的贡献统计

    Args:
        expert_id: 专家 ID

    Returns:
        贡献统计
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()

        # 统计专家贡献
        all_feedbacks = list(feedback_system.feedback_cache.values())
        expert_feedbacks = [f for f in all_feedbacks if f.expert_id == expert_id]

        # 按类型统计
        by_type = {}
        for f in expert_feedbacks:
            type_key = f.feedback_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

        # 按状态统计
        by_status = {}
        for f in expert_feedbacks:
            status_key = f.review_status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

        # 平均评分（如果专家提供了评分）
        ratings = [f.rating for f in expert_feedbacks if f.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            'expert_id': expert_id,
            'total_contributions': len(expert_feedbacks),
            'by_type': by_type,
            'by_status': by_status,
            'average_rating_given': round(avg_rating, 2),
            'approved_count': by_status.get('approved', 0),
            'implemented_count': by_status.get('implemented', 0)
        }

    except Exception as e:
        logger.error(f"获取专家贡献失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
