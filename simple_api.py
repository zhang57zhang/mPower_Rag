"""
简化的 FastAPI 服务
用于快速测试和基础功能验证
"""
import sys
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
            query=request.query,
            use_rerank=request.use_rerank
        )
        
        logger.info(f"Generated response with {len(result['sources'])} sources")
        return result
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档接口"""
    try:
        # 读取文件内容
        content = await file.read()
        text = content.decode("utf-8")
        
        # 创建文档对象
        document = Document(
            page_content=text,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            }
        )
        
        # 添加到 RAG 引擎
        rag_engine.add_documents([document])
        
        logger.info(f"Uploaded document: {file.filename}")
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "document_count": len(rag_engine.documents)
        }
        
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

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME} server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, log_level=settings.LOG_LEVEL.lower())