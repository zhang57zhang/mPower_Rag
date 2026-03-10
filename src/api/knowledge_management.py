"""
知识管理 API
提供文件导入、冲突检测、知识编辑等接口
"""
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import tempfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Knowledge Management"])


# ==================== 请求模型 ====================

class ImportRequest(BaseModel):
    """文件导入请求"""
    directory: Optional[str] = Field(None, description="目录路径")
    incremental: bool = Field(False, description="是否增量导入")
    auto_detect_conflicts: bool = Field(True, description="是否自动检测冲突")


class ConflictCheckRequest(BaseModel):
    """冲突检查请求"""
    document_ids: Optional[List[str]] = Field(None, description="要检查的文档ID列表")
    conflict_types: Optional[List[str]] = Field(
        None,
        description="冲突类型：factual, logical, temporal, authority, semantic"
    )


class KnowledgeUpdateRequest(BaseModel):
    """知识更新请求"""
    content: str = Field(..., description="更新后的内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    reason: Optional[str] = Field(None, description="更新原因")


# ==================== 响应模型 ====================

class ImportResponse(BaseModel):
    """文件导入响应"""
    imported: int
    skipped: int
    failed: int
    conflicts: List[Dict[str, Any]]
    message: str


class ConflictResponse(BaseModel):
    """冲突检查响应"""
    total_documents: int
    conflicts_found: int
    conflicts: List[Dict[str, Any]]


class KnowledgeStatsResponse(BaseModel):
    """知识统计响应"""
    total_documents: int
    total_chunks: int
    formats: Dict[str, int]
    last_updated: str


# ==================== API 接口 ====================

@router.post("/documents/import", response_model=ImportResponse)
async def import_documents(
    background_tasks: BackgroundTasks,
    files: Optional[List[UploadFile]] = File(None),
    request: ImportRequest = None
):
    """
    导入文档

    支持多种格式：TXT, MD, DOCX, XLSX, PDF, CSV, JSON, XML, PPTX, 图片（OCR）

    Args:
        background_tasks: 后台任务
        files: 上传的文件列表
        request: 导入请求参数

    Returns:
        导入结果
    """
    try:
        from data.enhanced_loader import get_enhanced_loader
        from core.vector_store import get_vector_store
        from core.embeddings import get_embeddings

        # 初始化组件
        loader = get_enhanced_loader()
        vector_store = get_vector_store()
        embeddings = get_embeddings()

        imported_count = 0
        skipped_count = 0
        failed_count = 0
        conflicts = []

        # 处理上传的文件
        if files:
            for file in files:
                try:
                    # 保存到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
                        shutil.copyfileobj(file.file, tmp)
                        tmp_path = tmp.name

                    # 加载文件
                    content, metadata = loader.load_file(tmp_path)

                    # 向量化并存储
                    doc_id = vector_store.add_document(
                        content=content,
                        metadata={
                            **metadata,
                            'filename': file.filename,
                            'source': 'upload'
                        }
                    )

                    imported_count += 1
                    logger.info(f"成功导入: {file.filename} -> {doc_id}")

                    # 清理临时文件
                    Path(tmp_path).unlink()

                except Exception as e:
                    failed_count += 1
                    logger.error(f"导入失败 {file.filename}: {e}")

        # 处理目录导入
        if request and request.directory:
            results = loader.load_directory(
                request.directory,
                recursive=True,
                incremental=request.incremental
            )

            for content, metadata in results:
                try:
                    doc_id = vector_store.add_document(
                        content=content,
                        metadata={
                            **metadata,
                            'source': 'directory'
                        }
                    )
                    imported_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"导入失败: {e}")

        # 自动检测冲突
        if request and request.auto_detect_conflicts and imported_count > 0:
            from core.conflict_detector import get_conflict_detector

            detector = get_conflict_detector(vector_store, embeddings)
            detected_conflicts = detector.detect_all_conflicts()

            conflicts = [
                {
                    'id': c.id,
                    'type': c.conflict_type.value,
                    'severity': c.severity.value,
                    'description': c.description,
                    'suggestion': c.suggestion
                }
                for c in detected_conflicts[:10]  # 只返回前10个
            ]

        return ImportResponse(
            imported=imported_count,
            skipped=skipped_count,
            failed=failed_count,
            conflicts=conflicts,
            message=f"成功导入 {imported_count} 个文档"
        )

    except Exception as e:
        logger.error(f"文档导入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/check-conflicts", response_model=ConflictResponse)
async def check_conflicts(request: ConflictCheckRequest):
    """
    检查知识冲突

    自动检测知识库中的矛盾和冲突

    Args:
        request: 冲突检查请求

    Returns:
        冲突检查结果
    """
    try:
        from core.vector_store import get_vector_store
        from core.embeddings import get_embeddings
        from core.conflict_detector import get_conflict_detector

        # 初始化组件
        vector_store = get_vector_store()
        embeddings = get_embeddings()
        detector = get_conflict_detector(vector_store, embeddings)

        # 检测冲突
        conflicts = detector.detect_all_conflicts(request.document_ids)

        # 过滤冲突类型
        if request.conflict_types:
            conflicts = [
                c for c in conflicts
                if c.conflict_type.value in request.conflict_types
            ]

        # 格式化响应
        formatted_conflicts = [
            {
                'id': c.id,
                'type': c.conflict_type.value,
                'severity': c.severity.value,
                'documents': c.documents,
                'description': c.description,
                'suggestion': c.suggestion,
                'confidence': c.confidence
            }
            for c in conflicts
        ]

        return ConflictResponse(
            total_documents=len(vector_store.get_all_documents()),
            conflicts_found=len(conflicts),
            conflicts=formatted_conflicts
        )

    except Exception as e:
        logger.error(f"冲突检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats", response_model=KnowledgeStatsResponse)
async def get_knowledge_stats():
    """
    获取知识统计

    Returns:
        知识库统计信息
    """
    try:
        from core.vector_store import get_vector_store

        vector_store = get_vector_store()
        documents = vector_store.get_all_documents()

        # 统计格式
        formats = {}
        for doc in documents:
            fmt = doc.get('metadata', {}).get('format', 'unknown')
            formats[fmt] = formats.get(fmt, 0) + 1

        # 获取最后更新时间
        last_updated = "unknown"
        if documents:
            timestamps = [
                doc.get('metadata', {}).get('modified_time', 0)
                for doc in documents
            ]
            if timestamps:
                from datetime import datetime
                last_updated = datetime.fromtimestamp(max(timestamps)).isoformat()

        return KnowledgeStatsResponse(
            total_documents=len(documents),
            total_chunks=sum(len(doc.get('content', '').split()) for doc in documents),
            formats=formats,
            last_updated=last_updated
        )

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/knowledge/{knowledge_id}")
async def update_knowledge(
    knowledge_id: str,
    request: KnowledgeUpdateRequest
):
    """
    更新知识

    支持在线编辑知识内容

    Args:
        knowledge_id: 知识 ID
        request: 更新请求

    Returns:
        更新结果
    """
    try:
        from core.vector_store import get_vector_store
        from core.expert_feedback import get_expert_feedback_system

        vector_store = get_vector_store()
        feedback_system = get_expert_feedback_system()

        # 获取原始知识
        old_knowledge = vector_store.get_document(knowledge_id)

        if not old_knowledge:
            raise HTTPException(status_code=404, detail="知识不存在")

        # 创建新版本
        version = feedback_system._create_knowledge_version(
            knowledge_id=knowledge_id,
            new_content=request.content,
            created_by="user",  # 实际应该从认证信息获取
            change_reason=request.reason or "手动更新"
        )

        # 更新向量存储
        vector_store.update_document(
            knowledge_id,
            content=request.content,
            metadata={
                **old_knowledge.get('metadata', {}),
                **(request.metadata or {}),
                'version': version.version_number,
                'last_modified': version.created_at
            }
        )

        return {
            'status': 'success',
            'knowledge_id': knowledge_id,
            'version': version.version_number,
            'message': '知识已更新'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{knowledge_id}/versions")
async def get_knowledge_versions(knowledge_id: str):
    """
    获取知识的所有版本

    Args:
        knowledge_id: 知识 ID

    Returns:
        版本列表
    """
    try:
        from core.expert_feedback import get_expert_feedback_system

        feedback_system = get_expert_feedback_system()
        versions = feedback_system.get_knowledge_versions(knowledge_id)

        return {
            'knowledge_id': knowledge_id,
            'versions': [
                {
                    'version_number': v.version_number,
                    'created_at': v.created_at,
                    'created_by': v.created_by,
                    'change_reason': v.change_reason,
                    'content_preview': v.content[:200] + '...' if len(v.content) > 200 else v.content
                }
                for v in versions
            ]
        }

    except Exception as e:
        logger.error(f"获取版本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/{knowledge_id}/rollback/{version_number}")
async def rollback_knowledge(knowledge_id: str, version_number: int):
    """
    回滚知识到指定版本

    Args:
        knowledge_id: 知识 ID
        version_number: 版本号

    Returns:
        回滚结果
    """
    try:
        from core.vector_store import get_vector_store
        from core.expert_feedback import get_expert_feedback_system

        vector_store = get_vector_store()
        feedback_system = get_expert_feedback_system()

        # 执行回滚
        success = feedback_system.rollback_knowledge(
            knowledge_id,
            version_number,
            vector_store
        )

        if success:
            return {
                'status': 'success',
                'knowledge_id': knowledge_id,
                'rolled_back_to': version_number,
                'message': f'已回滚到版本 {version_number}'
            }
        else:
            raise HTTPException(status_code=400, detail="回滚失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回滚失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str):
    """
    删除知识

    Args:
        knowledge_id: 知识 ID

    Returns:
        删除结果
    """
    try:
        from core.vector_store import get_vector_store

        vector_store = get_vector_store()

        # 删除知识
        success = vector_store.delete_document(knowledge_id)

        if success:
            return {
                'status': 'success',
                'knowledge_id': knowledge_id,
                'message': '知识已删除'
            }
        else:
            raise HTTPException(status_code=404, detail="知识不存在")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
