"""
FastAPI 主应用
提供 REST API 接口
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
from pathlib import Path
import json
import asyncio
import time
import uuid

from config.settings import settings
from core.rag_engine import get_rag_engine
from utils.cache import clear_all_cache
from core.vector_store import get_vector_store, VectorStoreManager
from core.embeddings import get_embeddings
from data.document_loader import get_document_manager
from core.conversation import get_conversation_manager

# 导入安全中间件
from api.middleware.auth import init_auth, verify_api_key, is_whitelisted, User
from api.middleware.rate_limit import init_rate_limiter, get_rate_limiter
from api.middleware.security import SecurityMiddleware, SecurityConfig

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="车载测试系统 RAG API",
)

# 安全中间件
security_config = SecurityConfig(
    cors_origins=settings.get_cors_origins(),
    cors_allow_credentials=settings.cors_allow_credentials,
    max_content_length=settings.max_content_length,
    max_query_length=settings.max_query_length,
)
app.add_middleware(SecurityMiddleware, config=security_config)

# CORS 中间件（使用配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件（在实际应用中应该在启动时初始化）
_embeddings = None
_vector_store: Optional[VectorStoreManager] = None
_rag_engine = None
_document_manager = None
_conversation_manager = None


def initialize_components():
    """初始化所有组件"""
    global _embeddings, _vector_store, _rag_engine, _document_manager, _conversation_manager

    try:
        # 初始化嵌入模型
        _embeddings = get_embeddings(provider="huggingface")

        # 初始化向量存储
        _vector_store = get_vector_store(
            db_type=settings.vector_db_type,
            collection_name=settings.qdrant_collection,
            embeddings=_embeddings,
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=getattr(settings, "qdrant_api_key", None),
        )

        # 初始化对话管理器
        _conversation_manager = get_conversation_manager(max_history=10)

        # 初始化 RAG 引擎（传入对话管理器和重排序配置）
        _rag_engine = get_rag_engine(
            vector_store=_vector_store,
            conversation_manager=_conversation_manager,
            llm_provider=settings.llm_provider,
            llm_model=settings.llm_model,
            llm_api_key=settings.llm_api_key,
            llm_base_url=settings.llm_base_url,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            use_rerank=settings.rerank_enabled,
            rerank_method=settings.rerank_method,
            rerank_model=settings.rerank_model,
        )

        # 初始化文档管理器
        _document_manager = get_document_manager(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        logger.info("所有组件初始化完成")

    except Exception as e:
        logger.error(f"组件初始化失败: {e}")
        raise


# API 模型


class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str = Field(..., description="用户问题")
    top_k: Optional[int] = Field(5, description="返回文档数量")
    context: Optional[Dict[str, Any]] = Field(None, description="额外上下文")
    use_rerank: Optional[bool] = Field(None, description="是否使用重排序（None 表示使用默认配置）")


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    question: str
    source_documents: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索关键词")
    top_k: Optional[int] = Field(5, description="返回结果数量")
    filter: Optional[Dict[str, Any]] = Field(None, description="过滤条件")


class UploadResponse(BaseModel):
    """上传响应模型"""
    message: str
    document_count: int
    chunk_count: int


# 对话管理模型


class CreateConversationRequest(BaseModel):
    """创建对话请求模型"""
    metadata: Optional[Dict[str, Any]] = Field(None, description="对话元数据")


class CreateConversationResponse(BaseModel):
    """创建对话响应模型"""
    conversation_id: str
    message: str


class SendMessageRequest(BaseModel):
    """发送消息请求模型"""
    question: str = Field(..., description="用户问题")
    top_k: Optional[int] = Field(5, description="返回文档数量")
    use_history: Optional[bool] = Field(True, description="是否使用对话历史")
    use_rerank: Optional[bool] = Field(None, description="是否使用重排序（None 表示使用默认配置）")


class SendMessageResponse(BaseModel):
    """发送消息响应模型"""
    answer: str
    question: str
    source_documents: List[Dict[str, Any]]
    conversation_id: str


class ConversationResponse(BaseModel):
    """对话响应模型"""
    id: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: Dict[str, Any]
    messages: List[Dict[str, Any]]


class ConversationsListResponse(BaseModel):
    """对话列表响应模型"""
    conversations: List[ConversationResponse]
    total: int


# 健康检查


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


# 问答接口


@app.post("/api/v1/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """问答接口"""
    try:
        if _rag_engine is None:
            raise HTTPException(status_code=503, detail="RAG 引擎未初始化")

        # 执行查询（传递重排序参数）
        result = _rag_engine.query_with_sources(
            question=request.question,
            top_k=request.top_k,
            use_rerank=request.use_rerank,
        )

        # 格式化源文档
        source_documents = []
        for doc_detail in result.get("source_details", []):
            source_documents.append({
                "content": doc_detail["content"][:200],  # 只返回前200字符
                "metadata": doc_detail["metadata"],
                "score": doc_detail["score"],
            })

        # 添加重排序信息到响应
        metadata = {}
        if result.get("reranked"):
            metadata["reranked"] = True
            metadata["rerank_method"] = result.get("rerank_method")

        return QueryResponse(
            answer=result["answer"],
            question=result["question"],
            source_documents=source_documents,
            metadata=metadata if metadata else None,
        )

    except Exception as e:
        logger.error(f"问答接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/search")
async def search(query: str, top_k: int = 5, score_threshold: float = None):
    """搜索接口"""
    try:
        if _vector_store is None:
            raise HTTPException(status_code=503, detail="向量存储未初始化")

        # 执行相似度搜索
        docs_with_scores = _vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
        )

        # 使用配置的阈值或传入的阈值
        threshold = score_threshold if score_threshold is not None else settings.retrieval_score_threshold

        # 格式化结果，并过滤低分结果
        results = []
        for doc, score in docs_with_scores:
            # 只保留相似度高于阈值的结果（注意：Chroma的距离越小越相似）
            # 对于余弦距离，score越小表示越相似
            if score <= (1 - threshold) * 500:  # 调整阈值计算方式
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                })

        # 如果没有找到相关文档，返回提示信息
        if not results:
            return {
                "results": [],
                "query": query,
                "message": "未找到与查询相关的知识原子信息，请尝试使用其他关键词或先上传更多文档。"
            }

        return {"results": results, "query": query}

    except Exception as e:
        logger.error(f"搜索接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 文档管理接口


@app.post("/api/v1/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    """上传文档接口"""
    try:
        if _document_manager is None or _vector_store is None:
            raise HTTPException(status_code=503, detail="文档管理器未初始化")

        # 保存上传的文件
        upload_dir = Path(settings.documents_path)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 加载并分割文档
        chunks = _document_manager.load_and_split(str(file_path))
        
        # 添加到向量库
        if chunks:
            ids = _vector_store.add_documents(chunks)
        
        return UploadResponse(
            message=f"文档 {file.filename} 上传成功",
            document_count=1,
            chunk_count=len(chunks),
        )

        # 添加到向量库
        if chunks:
            ids = _vector_store.add_documents(chunks)

        return UploadResponse(
            message=f"文档 {file.filename} 上传成功",
            document_count=1,
            chunk_count=len(chunks),
        )

    except Exception as e:
        logger.error(f"上传文档错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/documents/stats")
async def get_documents_stats():
    """获取文档统计信息"""
    try:
        if _vector_store is None:
            raise HTTPException(status_code=503, detail="向量存储未初始化")

        # 这里简化实现，实际应该从向量数据库获取统计信息
        stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "collections": [settings.qdrant_collection],
        }

        return stats

    except Exception as e:
        logger.error(f"获取文档统计错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 对话管理接口


@app.post("/api/v1/conversations", response_model=CreateConversationResponse)
async def create_conversation(request: CreateConversationRequest):
    """创建新对话"""
    try:
        if _conversation_manager is None:
            raise HTTPException(status_code=503, detail="对话管理器未初始化")

        # 创建对话
        conversation_id = _conversation_manager.create_conversation(
            metadata=request.metadata
        )

        return CreateConversationResponse(
            conversation_id=conversation_id,
            message="对话创建成功"
        )

    except Exception as e:
        logger.error(f"创建对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """获取对话详情"""
    try:
        if _conversation_manager is None:
            raise HTTPException(status_code=503, detail="对话管理器未初始化")

        # 获取对话
        conv = _conversation_manager.get_conversation(conversation_id)
        summary = _conversation_manager.get_conversation_summary(conversation_id)

        return ConversationResponse(
            id=conv["id"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
            message_count=summary["message_count"],
            metadata=conv["metadata"],
            messages=conv["messages"]
        )

    except ValueError as e:
        logger.error(f"对话不存在: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(conversation_id: str, request: SendMessageRequest):
    """发送消息到对话"""
    try:
        if _rag_engine is None or _conversation_manager is None:
            raise HTTPException(status_code=503, detail="RAG 引擎或对话管理器未初始化")

        # 验证对话是否存在
        try:
            _conversation_manager.get_conversation(conversation_id)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"对话不存在: {conversation_id}")

        # 执行查询（传入对话 ID 和重排序参数）
        result = _rag_engine.query_with_sources(
            question=request.question,
            top_k=request.top_k,
            use_rerank=request.use_rerank,
        )

        # 使用带对话历史的查询
        result_with_history = _rag_engine.query(
            question=request.question,
            conversation_id=conversation_id,
            use_history=request.use_history,
        )

        # 格式化源文档
        source_documents = []
        for doc_detail in result.get("source_details", []):
            source_documents.append({
                "content": doc_detail["content"][:200],  # 只返回前200字符
                "metadata": doc_detail["metadata"],
                "score": doc_detail["score"],
            })

        return SendMessageResponse(
            answer=result_with_history["answer"],
            question=result_with_history["question"],
            source_documents=source_documents,
            conversation_id=conversation_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送消息错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/conversations", response_model=ConversationsListResponse)
async def list_conversations(limit: int = 100):
    """列出所有对话"""
    try:
        if _conversation_manager is None:
            raise HTTPException(status_code=503, detail="对话管理器未初始化")

        # 获取对话列表
        conversations = _conversation_manager.list_conversations(limit=limit)

        # 转换为响应格式
        conversation_responses = []
        for conv in conversations:
            summary = _conversation_manager.get_conversation_summary(conv["id"])
            conversation_responses.append(ConversationResponse(
                id=conv["id"],
                created_at=conv["created_at"],
                updated_at=conv["updated_at"],
                message_count=summary["message_count"],
                metadata=conv["metadata"],
                messages=conv["messages"]
            ))

        return ConversationsListResponse(
            conversations=conversation_responses,
            total=len(conversation_responses)
        )

    except Exception as e:
        logger.error(f"列出对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    try:
        if _conversation_manager is None:
            raise HTTPException(status_code=503, detail="对话管理器未初始化")

        # 删除对话
        _conversation_manager.delete_conversation(conversation_id)

        return {"message": "对话删除成功"}

    except ValueError as e:
        logger.error(f"对话不存在: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 评估接口模型


class EvaluateRequest(BaseModel):
    """评估请求模型"""
    dataset_path: str = Field("tests/eval_dataset.json", description="评估数据集路径")
    use_rerank: Optional[bool] = Field(None, description="是否使用重排序")


class EvaluateResponse(BaseModel):
    """评估响应模型"""
    dataset_name: str
    total_questions: int
    evaluated: int
    results: List[Dict[str, Any]]
    summary: Dict[str, float]


class EvaluationResult(BaseModel):
    """单个评估结果"""
    id: int
    question: str
    expected_answer: str
    generated_answer: str
    relevance_score: float
    accuracy_score: float
    completeness_score: float
    fluency_score: float
    overall_score: float
    source_count: int


class EvaluateSummary(BaseModel):
    """评估摘要"""
    avg_relevance: float
    avg_accuracy: float
    avg_completeness: float
    avg_fluency: float
    avg_overall: float
    passed_count: int
    total_count: int
    pass_rate: float


# 流式输出接口模型


class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    question: str = Field(..., description="用户问题")
    conversation_id: Optional[str] = Field(None, description="对话 ID")
    use_history: Optional[bool] = Field(True, description="是否使用对话历史")
    use_rerank: Optional[bool] = Field(None, description="是否使用重排序")
    top_k: Optional[int] = Field(5, description="返回文档数量")


class StreamChunk(BaseModel):
    """流式响应块"""
    content: str = Field(..., description="生成的文本内容")
    done: bool = Field(False, description="是否完成")
    source_documents: Optional[List[Dict[str, Any]]] = Field(None, description="源文档（仅在最后一块返回）")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据（仅在最后一块返回）")


# 评估接口


@app.post("/api/v1/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest):
    """执行评估"""
    try:
        if _rag_engine is None:
            raise HTTPException(status_code=503, detail="RAG 引擎未初始化")

        # 导入评估器
        from core.evaluation import RAGEvaluator

        # 创建评估器
        evaluator = RAGEvaluator()

        # 加载数据集
        import json
        with open(request.dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        # 执行评估
        results = []
        summary = {
            "avg_relevance": 0.0,
            "avg_accuracy": 0.0,
            "avg_completeness": 0.0,
            "avg_fluency": 0.0,
            "avg_overall": 0.0,
            "passed_count": 0,
            "total_count": 0,
            "pass_rate": 0.0,
        }

        total_questions = len(dataset.get("data", []))
        evaluated_count = 0

        for item in dataset.get("data", []):
            try:
                # 执行查询
                result = _rag_engine.query_with_sources(
                    question=item["question"],
                    top_k=5,
                    use_rerank=request.use_rerank,
                )

                # 评估结果
                eval_result = evaluator.evaluate(
                    question=item["question"],
                    expected_answer=item["expected_answer"],
                    generated_answer=result["answer"],
                    source_documents=result.get("source_details", []),
                )

                results.append(eval_result)

                # 更新统计
                for key in ["relevance", "accuracy", "completeness", "fluency", "overall"]:
                    summary[f"avg_{key}"] += eval_result[f"{key}_score"]

                if eval_result["overall_score"] >= 0.6:
                    summary["passed_count"] += 1

                evaluated_count += 1

            except Exception as e:
                logger.error(f"评估问题 {item['id']} 失败: {e}")
                continue

        # 计算平均值
        if evaluated_count > 0:
            for key in ["relevance", "accuracy", "completeness", "fluency", "overall"]:
                summary[f"avg_{key}"] = summary[f"avg_{key}"] / evaluated_count

            summary["total_count"] = evaluated_count
            summary["pass_rate"] = (summary["passed_count"] / evaluated_count) * 100

        return EvaluateResponse(
            dataset_name=dataset.get("dataset_name", "Unknown"),
            total_questions=total_questions,
            evaluated=evaluated_count,
            results=results,
            summary=summary,
        )

    except Exception as e:
        logger.error(f"评估接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/evaluations")
async def list_evaluations():
    """查看评估历史"""
    try:
        # 这里简化实现，返回空列表
        # 实际应该从数据库或文件中读取历史评估
        return {
            "evaluations": [],
            "total": 0,
        }

    except Exception as e:
        logger.error(f"列出评估错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/evaluations/stats")
async def get_evaluation_stats():
    """评估统计"""
    try:
        # 这里简化实现
        stats = {
            "total_evaluations": 0,
            "avg_overall_score": 0.0,
            "last_evaluation": None,
        }

        return stats

    except Exception as e:
        logger.error(f"获取评估统计错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 流式输出接口


@app.post("/api/v1/chat/stream")
async def stream_chat(request: StreamChatRequest):
    """流式聊天接口（SSE）
    
    Returns:
        Server-Sent Events 流式响应
    """
    if _rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG 引擎未初始化")

    async def generate_response() -> AsyncGenerator[str, None]:
        """异步生成流式响应（SSE 格式）"""
        try:
            # 执行查询
            result = _rag_engine.query_with_sources(
                question=request.question,
                top_k=request.top_k,
                use_rerank=request.use_rerank,
            )

            # 检索相关文档
            docs_with_scores = _vector_store.similarity_search_with_score(
                query=request.question,
                k=request.top_k,
            )

            # SSE 格式：data: {...}\n\n
            # 发送第一个 chunk：问题
            yield f"data: {json.dumps({'type': 'question', 'content': result['question']}, ensure_ascii=False)}\n\n"

            # 流式发送答案
            answer = result["answer"]
            chunk_size = 20  # 每次发送的字符数

            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i + chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'content': chunk, 'done': False}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)  # 小延迟，确保客户端有时间处理

            # 发送最后一个 chunk：完成信号和源文档
            source_docs = []
            for doc, score in docs_with_scores:
                source_docs.append({
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata,
                    "score": float(score),
                })

            final_data = {
                "type": "done",
                "content": "",
                "done": True,
                "source_documents": source_docs,
                "metadata": {
                    "reranked": result.get("reranked", False),
                    "rerank_method": result.get("rerank_method"),
                    "source_count": len(source_docs),
                },
            }
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"流式生成错误: {e}")
            error_data = {
                "type": "error",
                "content": f"生成失败：{str(e)}",
                "done": True,
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


# 缓存管理接口


class CacheStatsResponse(BaseModel):
    """缓存统计响应模型"""
    enabled: bool = Field(False, description="缓存是否启用")
    connected: bool = Field(False, description="Redis 连接状态")
    total_keys: int = Field(0, description="总键数")
    prefix_counts: Dict[str, int] = Field(default_factory=dict, description="各前缀的键数")


class ClearCacheRequest(BaseModel):
    """清空缓存请求模型"""
    prefix: Optional[str] = Field(None, description="清空指定前缀（query, retrieval, llm, rerank, null 表示全部）")


class ClearCacheResponse(BaseModel):
    """清空缓存响应模型"""
    message: str = Field(..., description="操作消息")
    cleared_count: int = Field(0, description="清空的缓存数量")


@app.get("/api/v1/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats_endpoint():
    """获取缓存统计"""
    try:
        from core.api.cache_management import get_cache_stats

        stats = get_cache_stats()
        return CacheStatsResponse(**stats)

    except Exception as e:
        logger.error(f"获取缓存统计错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/cache/clear", response_model=ClearCacheResponse)
async def clear_cache_endpoint(request: ClearCacheRequest):
    """清空缓存"""
    try:
        from core.api.cache_management import clear_cache as clear_cache_func

        result = clear_cache_func(request.prefix)
        return ClearCacheResponse(**result)

    except Exception as e:
        logger.error(f"清空缓存错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/cache/clear_all", response_model=ClearCacheResponse)
async def clear_all_cache_endpoint():
    """清空所有缓存"""
    try:
        from core.utils.cache import clear_all_cache

        result = clear_all_cache()
        return ClearCacheResponse(
            message="已清空所有缓存" if result else "清空失败",
            cleared_count=result if result else 0,
        )

    except Exception as e:
        logger.error(f"清空所有缓存错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 增强健康检查


class HealthStatus(BaseModel):
    """健康状态响应"""
    status: str = "healthy"
    app_name: str
    version: str
    components: Dict[str, Any] = {}
    timestamp: float


@app.get("/health", response_model=HealthStatus)
@app.get("/health/live", response_model=HealthStatus)
async def health_check():
    """健康检查接口（存活探针）"""
    return HealthStatus(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=time.time(),
    )


@app.get("/health/ready", response_model=HealthStatus)
async def readiness_check():
    """就绪探针（检查所有依赖）"""
    components = {}

    # 检查向量存储
    components["vector_store"] = {
        "status": "ready" if _vector_store is not None else "not_ready"
    }

    # 检查 RAG 引擎
    components["rag_engine"] = {
        "status": "ready" if _rag_engine is not None else "not_ready"
    }

    # 检查对话管理器
    components["conversation_manager"] = {
        "status": "ready" if _conversation_manager is not None else "not_ready"
    }

    # 检查 Redis（如果启用缓存）
    if settings.cache_enabled:
        try:
            from core.utils.cache import _cache_instance
            components["redis"] = {
                "status": "ready" if _cache_instance and _cache_instance.redis_client else "not_ready"
            }
        except Exception:
            components["redis"] = {"status": "error"}

    # 计算整体状态
    all_ready = all(
        c.get("status") in ["ready", "healthy"]
        for c in components.values()
    )

    return HealthStatus(
        status="ready" if all_ready else "not_ready",
        app_name=settings.app_name,
        version=settings.app_version,
        components=components,
        timestamp=time.time(),
    )


# Prometheus 指标端点


@app.get("/metrics")
async def metrics():
    """Prometheus 指标端点"""
    if not settings.prometheus_enabled:
        raise HTTPException(status_code=404, detail="Prometheus metrics not enabled")

    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="prometheus_client not installed")


# 启动事件


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")

    # 初始化认证
    if settings.api_auth_enabled:
        api_keys = settings.get_api_keys()
        admin_keys = settings.get_admin_api_keys()
        init_auth(api_keys, admin_keys)
        logger.info(f"API 认证已启用，有效 Key 数量: {len(api_keys)}")
    else:
        logger.warning("API 认证未启用（开发模式）")

    # 初始化限流器
    if settings.rate_limit_enabled:
        init_rate_limiter(
            requests_per_minute=settings.rate_limit_requests_per_minute,
            burst_size=settings.rate_limit_burst_size,
            enabled=True
        )

    # 初始化核心组件
    initialize_components()

    logger.info("所有组件初始化完成，服务就绪")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"{settings.app_name} 正在关闭...")

    # 清理资源
    global _embeddings, _vector_store, _rag_engine, _document_manager, _conversation_manager
    _embeddings = None
    _vector_store = None
    _rag_engine = None
    _document_manager = None
    _conversation_manager = None

    logger.info("资源清理完成")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
