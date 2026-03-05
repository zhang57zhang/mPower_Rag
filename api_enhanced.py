#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 FastAPI 服务
支持文档管理、外部API调用
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import tempfile
import shutil

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from simple_config import settings, Document
from simple_rag_engine import get_rag_engine, clear_all_cache
from document_manager import DocumentManager
from external_api import (
    ExternalAPIHandler, 
    ExternalQueryRequest, 
    ExternalDocumentUpload,
    ExternalBatchQueryRequest
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=f"{settings.APP_NAME} (Enhanced)",
    version=f"{settings.APP_VERSION}-enhanced",
    description="车载测试系统 RAG API - 支持文档管理和外部API调用",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class QueryRequest(BaseModel):
    query: str
    use_rerank: bool = False
    top_k: int = 5

class DocumentUploadRequest(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class HealthResponse(BaseModel):
    status: str
    message: str

# 初始化组件
try:
    rag_engine = get_rag_engine(use_local=True)
    logger.info("RAG engine initialized with local vector store")
except Exception as e:
    logger.error(f"Failed to initialize RAG engine: {e}")
    rag_engine = None

try:
    document_manager = DocumentManager(
        knowledge_base_dir=getattr(settings, 'KNOWLEDGE_BASE_DIR', 'knowledge_base')
    )
    logger.info("Document manager initialized")
except Exception as e:
    logger.error(f"Failed to initialize document manager: {e}")
    document_manager = None

try:
    external_api_handler = ExternalAPIHandler(rag_engine, document_manager)
    logger.info("External API handler initialized")
except Exception as e:
    logger.error(f"Failed to initialize external API handler: {e}")
    external_api_handler = None

# 启动时自动加载知识库
try:
    from startup_loader import load_knowledge_on_startup
    load_knowledge_on_startup()
except Exception as e:
    logger.warning(f"Startup knowledge loading failed: {e}")

# ==================== 基础接口 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"{settings.APP_NAME} API (Enhanced)",
        "version": f"{settings.APP_VERSION}-enhanced",
        "features": ["document_management", "external_api", "multi_format_support"]
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    health = rag_engine.health_check() if rag_engine else {"status": "unhealthy"}
    
    # 检查文档管理器
    doc_manager_status = "healthy" if document_manager else "unavailable"
    
    return {
        "status": health["status"],
        "message": "API is running" if health["status"] == "healthy" else "API is not fully initialized",
        "components": {
            "rag_engine": health["status"],
            "document_manager": doc_manager_status,
            "external_api": "available" if external_api_handler else "unavailable"
        }
    }

# ==================== 查询接口 ====================

@app.post("/api/v1/chat")
async def chat(request: QueryRequest):
    """智能问答接口"""
    try:
        logger.info(f"Received query: {request.query}")
        
        result = rag_engine.query_with_sources(
            query=request.query,
            use_rerank=request.use_rerank
        )
        
        logger.info(f"Generated response with {len(result['sources'])} sources")
        
        return {
            "answer": result["answer"],
            "sources": result["sources"][:request.top_k],
            "metadata": {
                "engine": result.get("engine", "unknown"),
                "use_rerank": request.use_rerank
            }
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 文档管理接口 ====================

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = "general"
):
    """
    上传文档（支持多种格式）
    
    支持: .txt, .md, .docx, .xlsx, .pdf
    """
    try:
        logger.info(f"Uploading document: {file.filename}, category: {category}")
        
        # 保存上传的文件到临时位置
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
        
        try:
            # 使用文档管理器处理
            result = document_manager.upload_document(
                file_path=tmp_path,
                category=category,
                metadata={"original_filename": file.filename}
            )
            
            if result["success"]:
                # 添加到RAG引擎
                rag_engine.add_document(
                    content=result["content"],
                    metadata={
                        "doc_id": result["doc_id"],
                        "filename": file.filename,
                        "category": category
                    }
                )
                
                logger.info(f"Document uploaded and added to RAG: {result['doc_id']}")
                
                return {
                    "success": True,
                    "doc_id": result["doc_id"],
                    "filename": file.filename,
                    "category": category,
                    "content_length": result["content_length"],
                    "message": "Document uploaded successfully"
                }
            else:
                raise HTTPException(status_code=400, detail=result["error"])
                
        finally:
            # 清理临时文件
            if tmp_path.exists():
                tmp_path.unlink()
                
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/documents/upload-text")
async def upload_text_document(request: ExternalDocumentUpload):
    """
    上传文本内容（直接提供文本）
    
    用于外部API调用
    """
    try:
        result = await external_api_handler.upload_document(request)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Text document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    try:
        result = await external_api_handler.delete_document(doc_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Document {doc_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents")
async def list_documents(
    category: Optional[str] = None,
    format: Optional[str] = None
):
    """列出所有文档"""
    try:
        documents = await external_api_handler.list_documents(
            category=category,
            format=format
        )
        
        return {
            "success": True,
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/{doc_id}")
async def get_document(doc_id: str):
    """获取文档详情"""
    try:
        document = await external_api_handler.get_document(doc_id)
        
        if document:
            return {
                "success": True,
                "document": document
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except Exception as e:
        logger.error(f"Get document failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/formats")
async def get_supported_formats():
    """获取支持的文档格式"""
    formats = document_manager.get_supported_formats()
    
    return {
        "supported_formats": formats,
        "description": {
            "txt": "Plain text file",
            "md": "Markdown file",
            "docx": "Microsoft Word document (requires python-docx)",
            "xlsx": "Microsoft Excel spreadsheet (requires openpyxl)",
            "pdf": "PDF document (requires PyPDF2)"
        }
    }

# ==================== 外部API接口 ====================

@app.post("/api/v1/external/query")
async def external_query(request: ExternalQueryRequest):
    """
    外部API查询接口
    
    供外部系统调用的标准化查询接口
    """
    try:
        response = await external_api_handler.query(request)
        return response
    except Exception as e:
        logger.error(f"External query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/external/batch-query")
async def external_batch_query(request: ExternalBatchQueryRequest):
    """
    外部API批量查询接口
    
    支持一次提交多个查询
    """
    try:
        response = await external_api_handler.batch_query(request)
        return response
    except Exception as e:
        logger.error(f"External batch query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 系统管理接口 ====================

@app.post("/api/v1/system/clear-cache")
async def clear_cache():
    """清除缓存"""
    try:
        clear_all_cache()
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Clear cache failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/stats")
async def get_system_stats():
    """获取系统统计信息"""
    try:
        # 获取文档统计
        documents = document_manager.list_documents()
        
        # 获取支持的格式
        formats = document_manager.get_supported_formats()
        
        return {
            "documents": {
                "total": len(documents),
                "by_category": {},  # TODO: 实现分类统计
                "by_format": {}  # TODO: 实现格式统计
            },
            "supported_formats": formats,
            "rag_engine": {
                "status": "healthy" if rag_engine else "unavailable",
                "type": "local"
            }
        }
        
    except Exception as e:
        logger.error(f"Get system stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 60)
    logger.info(f"{settings.APP_NAME} API (Enhanced) starting...")
    logger.info("=" * 60)
    logger.info(f"RAG Engine: {'✓' if rag_engine else '✗'}")
    logger.info(f"Document Manager: {'✓' if document_manager else '✗'}")
    logger.info(f"External API Handler: {'✓' if external_api_handler else '✗'}")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
