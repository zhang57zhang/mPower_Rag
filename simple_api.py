"""
简化的 FastAPI 服务
用于快速测试和基础功能验证
支持多格式文档上传、删除和外部API集成
"""
import sys
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from simple_config import settings, Document
from simple_rag_engine import get_rag_engine, clear_all_cache
from document_parser import DocumentParser, is_format_supported, get_supported_formats
from external_api import ExternalAPIClient, fetch_from_external_api

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="车载测试系统 RAG API (简化版)",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
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

class DeleteDocumentsRequest(BaseModel):
    doc_ids: List[str]

class ImportFromAPIRequest(BaseModel):
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ImportDirectoryRequest(BaseModel):
    directory_path: str
    recursive: bool = False
    file_extensions: Optional[List[str]] = None

# 初始化 RAG 引擎（使用本地向量引擎，快速启动）
try:
    rag_engine = get_rag_engine(use_local=True)
    logger.info("RAG engine initialized with local vector store")
except Exception as e:
    logger.error(f"Failed to initialize RAG engine: {e}")
    rag_engine = None

# 启动时自动加载知识库
load_knowledge_on_startup = None
try:
    from startup_loader import load_knowledge_on_startup as loader
    load_knowledge_on_startup = loader
    load_knowledge_on_startup()
except Exception as e:
    print(f"启动时加载知识库失败: {e}")
    print("API服务将继续运行，但需要手动上传文档")

@app.get("/")
async def root():
    """根路径"""
    return {"message": f"{settings.APP_NAME} API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    """健康检查"""
    health = rag_engine.health_check()
    return HealthResponse(
        status=health["status"],
        message="API is running" if health["status"] == "healthy" else "API is not fully initialized"
    )

@app.post("/api/v1/chat")
async def chat(request: QueryRequest):
    """智能问答接口"""
    try:
        logger.info(f"Received query: {request.query}")

        # 执行查询
        result = rag_engine.query_with_sources(
            query=request.query
        )

        logger.info(f"Generated response with {len(result['sources'])} sources")
        return result

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档接口（支持多格式：txt/md/docx/xlsx/pdf）"""
    try:
        # 检查文件格式
        if not is_format_supported(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持的格式: {list(get_supported_formats().keys())}"
            )

        # 读取文件内容
        content = await file.read()

        # 解析文档
        text, metadata = DocumentParser.parse(content, file.filename)

        # 添加用户提供的元数据
        metadata.update({
            "content_type": file.content_type,
            "upload_method": "file_upload",
        })

        # 创建文档对象
        document = Document(page_content=text, metadata=metadata)

        # 添加到 RAG 引擎
        rag_engine.add_documents([document])

        logger.info(f"Uploaded document: {file.filename} (format: {metadata['format']})")

        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "format": metadata['format'],
            "size": len(content),
            "document_count": len(rag_engine.documents)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """应用启动时的处理"""
    if load_knowledge_on_startup:
        load_knowledge_on_startup()

@app.get("/api/v1/documents/stats")
async def get_document_stats():
    """获取文档统计信息"""
    try:
        return {
            "total_documents": len(rag_engine.documents),
            "engine_status": rag_engine.health_check(),
            "config": {
                "top_k": settings.TOP_K,
                "chunk_size": settings.CHUNK_SIZE,
                "rerank_enabled": settings.RERANK_ENABLED,
                "cache_enabled": settings.CACHE_ENABLED
            }
        }
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.post("/api/v1/clear")
async def clear_cache():
    """清除缓存"""
    try:
        clear_all_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

# 示例问题和测试数据
@app.get("/api/v1/examples")
async def get_examples():
    """获取示例问题"""
    return {
        "examples": [
            "车载蓝牙模块的连接稳定性测试方法",
            "ECU故障诊断流程是什么？",
            "如何进行发动机性能测试？",
            "CAN总线通信测试标准"
        ],
        "note": "这些都是示例问题，实际系统需要有相关的知识库文档才能回答"
    }


# ==================== 新增接口 ====================

@app.get("/api/v1/documents/list")
async def list_documents():
    """列出所有文档"""
    try:
        docs = rag_engine.list_documents()
        return {
            "total": len(docs),
            "documents": docs
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.delete("/api/v1/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除单个文档"""
    try:
        success = rag_engine.remove_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")

        logger.info(f"Deleted document: {doc_id}")
        return {
            "message": "Document deleted successfully",
            "doc_id": doc_id,
            "remaining_documents": len(rag_engine.documents)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@app.post("/api/v1/documents/batch-delete")
async def batch_delete_documents(request: DeleteDocumentsRequest):
    """批量删除文档"""
    try:
        results = rag_engine.remove_documents_batch(request.doc_ids)

        success_count = sum(1 for v in results.values() if v)
        failed_count = len(results) - success_count

        logger.info(f"Batch delete completed: {success_count} success, {failed_count} failed")

        return {
            "message": f"Batch delete completed: {success_count} success, {failed_count} failed",
            "results": results,
            "success_count": success_count,
            "failed_count": failed_count,
            "remaining_documents": len(rag_engine.documents)
        }

    except Exception as e:
        logger.error(f"Error batch deleting documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error batch deleting documents: {str(e)}")


@app.get("/api/v1/formats")
async def get_supported_document_formats():
    """获取支持的文档格式"""
    return {
        "supported_formats": get_supported_formats(),
        "description": "系统支持上传以下格式的文档"
    }


@app.post("/api/v1/documents/import-from-api")
async def import_from_external_api(request: ImportFromAPIRequest):
    """从外部API导入文档"""
    try:
        # 从外部API获取文档
        result = fetch_from_external_api(
            url=request.url,
            headers=request.headers,
            params=request.params
        )

        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch from external API: {result.get('error', 'Unknown error')}"
            )

        # 创建文档对象
        metadata = result['metadata']
        if request.metadata:
            metadata.update(request.metadata)

        document = Document(
            page_content=result['content'],
            metadata=metadata
        )

        # 添加到RAG引擎
        rag_engine.add_documents([document])

        logger.info(f"Imported document from external API: {request.url}")

        return {
            "message": "Document imported successfully from external API",
            "source_url": request.url,
            "content_length": len(result['content']),
            "document_count": len(rag_engine.documents)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing from external API: {e}")
        raise HTTPException(status_code=500, detail=f"Error importing from external API: {str(e)}")


@app.post("/api/v1/query-from-external")
async def query_for_external_system(request: QueryRequest):
    """
    外部系统查询接口
    与/api/v1/chat功能相同，但明确用于外部系统调用
    """
    try:
        logger.info(f"External query received: {request.query}")

        # 执行查询
        result = rag_engine.query_with_sources(
            query=request.query
        )

        # 添加额外信息供外部系统使用
        result['api_version'] = settings.APP_VERSION
        result['query_timestamp'] = time.time()

        logger.info(f"External query completed: {len(result['sources'])} sources")
        return result

    except Exception as e:
        logger.error(f"Error in external query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== Phase 2 新增接口 ====================

@app.post("/api/v1/documents/batch-upload")
async def batch_upload_documents(files: List[UploadFile] = File(...)):
    """
    批量上传文档
    支持多格式文档批量上传
    """
    try:
        results = []
        success_count = 0
        failed_count = 0

        for file in files:
            try:
                # 检查文件格式
                if not is_format_supported(file.filename):
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": f"不支持的文件格式"
                    })
                    failed_count += 1
                    continue

                # 读取文件内容
                content = await file.read()

                # 文档大小限制检查（10MB）
                max_size = 10 * 1024 * 1024  # 10MB
                if len(content) > max_size:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": f"文件过大，最大支持{max_size // (1024*1024)}MB"
                    })
                    failed_count += 1
                    continue

                # 解析文档
                text, metadata = DocumentParser.parse(content, file.filename)
                metadata.update({
                    "content_type": file.content_type,
                    "upload_method": "batch_upload",
                })

                # 创建文档对象
                document = Document(page_content=text, metadata=metadata)

                # 添加到 RAG 引擎
                rag_engine.add_documents([document])

                results.append({
                    "filename": file.filename,
                    "success": True,
                    "format": metadata['format'],
                    "size": len(content)
                })
                success_count += 1

            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
                failed_count += 1

        logger.info(f"Batch upload completed: {success_count} success, {failed_count} failed")

        return {
            "message": f"批量上传完成: {success_count} 成功, {failed_count} 失败",
            "success_count": success_count,
            "failed_count": failed_count,
            "total_documents": len(rag_engine.documents),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        raise HTTPException(status_code=500, detail=f"Error in batch upload: {str(e)}")


@app.post("/api/v1/documents/import-directory")
async def import_directory(request: ImportDirectoryRequest):
    """
    导入整个目录的文档
    支持递归扫描和文件扩展名过滤
    """
    try:
        from pathlib import Path

        directory = Path(request.directory_path)

        # 检查目录是否存在
        if not directory.exists():
            raise HTTPException(status_code=400, detail=f"目录不存在: {request.directory_path}")

        if not directory.is_dir():
            raise HTTPException(status_code=400, detail=f"路径不是目录: {request.directory_path}")

        # 确定要扫描的文件扩展名
        if request.file_extensions:
            extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in request.file_extensions]
        else:
            extensions = list(get_supported_formats().keys())

        # 扫描文件
        files = []
        if request.recursive:
            for ext in extensions:
                files.extend(directory.rglob(f"*{ext}"))
        else:
            for ext in extensions:
                files.extend(directory.glob(f"*{ext}"))

        # 过滤掉目录
        files = [f for f in files if f.is_file()]

        if not files:
            return {
                "message": "未找到符合条件的文档",
                "directory": str(directory),
                "scanned_extensions": extensions,
                "recursive": request.recursive,
                "files_found": 0,
                "imported_count": 0
            }

        # 导入文档
        results = []
        success_count = 0
        failed_count = 0

        for file_path in files:
            try:
                # 读取文件内容
                with open(file_path, 'rb') as f:
                    content = f.read()

                # 文档大小限制检查（10MB）
                max_size = 10 * 1024 * 1024
                if len(content) > max_size:
                    results.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "success": False,
                        "error": f"文件过大，最大支持{max_size // (1024*1024)}MB"
                    })
                    failed_count += 1
                    continue

                # 解析文档
                text, metadata = DocumentParser.parse(content, file_path.name)
                metadata.update({
                    "file_path": str(file_path),
                    "import_method": "directory_import",
                })

                # 创建文档对象
                document = Document(page_content=text, metadata=metadata)

                # 添加到 RAG 引擎
                rag_engine.add_documents([document])

                results.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "success": True,
                    "format": metadata['format'],
                    "size": len(content)
                })
                success_count += 1

            except Exception as e:
                results.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "success": False,
                    "error": str(e)
                })
                failed_count += 1

        logger.info(f"Directory import completed: {success_count} success, {failed_count} failed")

        return {
            "message": f"目录导入完成: {success_count} 成功, {failed_count} 失败",
            "directory": str(directory),
            "recursive": request.recursive,
            "scanned_extensions": extensions,
            "files_found": len(files),
            "imported_count": success_count,
            "failed_count": failed_count,
            "total_documents": len(rag_engine.documents),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing directory: {e}")
        raise HTTPException(status_code=500, detail=f"Error importing directory: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME} server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, log_level=settings.LOG_LEVEL.lower())