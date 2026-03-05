"""
增强的 RAG 引擎 - 支持向量检索和关键词检索
"""
from typing import List, Dict, Any, Optional
import logging
import hashlib
from pathlib import Path
from simple_config import settings, Document
from vector_search import VectorSearchEngine

logger = logging.getLogger(__name__)


class EnhancedRAGEngine:
    """增强的 RAG 引擎（支持向量检索）"""

    def __init__(self, use_vector: bool = True):
        """初始化引擎"""
        self.use_vector = use_vector
        self.documents = []  # 关键词检索用
        self.document_ids = {}  # 文档ID映射 {doc_id: index}
        self.vector_engine = None  # 向量检索引擎
        self.is_initialized = False
        self.llm_client = None

    def initialize(self):
        """初始化引擎"""
        try:
            # 初始化向量搜索引擎
            if self.use_vector:
                try:
                    self.vector_engine = VectorSearchEngine(
                        host=settings.QDRANT_HOST,
                        port=settings.QDRANT_PORT,
                        collection_name=settings.QDRANT_COLLECTION_NAME
                    )
                    logger.info("向量搜索引擎初始化成功")
                except Exception as e:
                    logger.warning(f"向量搜索引擎初始化失败，将使用关键词检索: {e}")
                    self.use_vector = False

            self.is_initialized = True
            logger.info("Enhanced RAG Engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {e}")
            return False

    def add_documents(self, documents: List[Document]):
        """添加文档到知识库"""
        for doc in documents:
            # 生成唯一ID
            doc_id = self._generate_doc_id(doc)
            doc_index = len(self.documents)

            # 添加到文档列表
            self.documents.append(doc)
            self.document_ids[doc_id] = doc_index

            # 添加到向量数据库
            if self.vector_engine:
                vector_doc = {
                    "id": doc_id,
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", ""),
                    "metadata": doc.metadata
                }
                self.vector_engine.add_documents([vector_doc])

        logger.info(f"添加了 {len(documents)} 个文档到知识库")

    def _generate_doc_id(self, doc: Document) -> str:
        """生成文档唯一ID"""
        content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()[:8]
        source = doc.metadata.get("filename", doc.metadata.get("source", "unknown"))
        # 清理source中的特殊字符
        source = source.replace(".", "_").replace(" ", "_")[:20]
        return f"{source}_{content_hash}"

    def remove_document(self, doc_id: str) -> bool:
        """
        删除单个文档

        Args:
            doc_id: 文档ID

        Returns:
            是否删除成功
        """
        if doc_id not in self.document_ids:
            logger.warning(f"文档不存在: {doc_id}")
            return False

        try:
            # 获取文档索引
            doc_index = self.document_ids[doc_id]

            # 从文档列表中删除
            self.documents.pop(doc_index)

            # 从ID映射中删除
            del self.document_ids[doc_id]

            # 更新索引映射（因为删除了一个文档，后面的索引都要-1）
            for id_key in list(self.document_ids.keys()):
                if self.document_ids[id_key] > doc_index:
                    self.document_ids[id_key] -= 1

            # 从向量数据库中删除
            if self.vector_engine:
                self.vector_engine.delete_document(doc_id)

            logger.info(f"成功删除文档: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False

    def remove_documents_batch(self, doc_ids: List[str]) -> Dict[str, bool]:
        """
        批量删除文档

        Args:
            doc_ids: 文档ID列表

        Returns:
            {doc_id: 是否成功}
        """
        results = {}
        for doc_id in doc_ids:
            results[doc_id] = self.remove_document(doc_id)

        success_count = sum(1 for v in results.values() if v)
        logger.info(f"批量删除完成: {success_count}/{len(doc_ids)} 成功")
        return results

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        列出所有文档

        Returns:
            文档列表，每个文档包含id和metadata
        """
        docs = []
        for doc_id, doc_index in self.document_ids.items():
            doc = self.documents[doc_index]
            docs.append({
                "id": doc_id,
                "metadata": doc.metadata,
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content,
            })
        return docs

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似文档（向量检索 + 关键词检索）"""

        results = []

        # 向量检索
        if self.vector_engine and self.use_vector:
            try:
                vector_results = self.vector_engine.search(
                    query=query,
                    top_k=top_k,
                    score_threshold=0.3  # 降低阈值以获取更多结果
                )

                for result in vector_results:
                    results.append({
                        "content": result["content"],
                        "metadata": result["metadata"],
                        "score": result["score"],
                        "method": "vector"
                    })
            except Exception as e:
                logger.warning(f"向量检索失败: {e}")

        # 关键词检索（作为补充）
        keyword_results = self._keyword_search(query, top_k)
        for result in keyword_results:
            # 避免重复
            if not any(r["content"] == result["content"] for r in results):
                results.append(result)

        # 合并并排序（向量检索优先）
        results.sort(key=lambda x: (x.get("method") == "vector", x["score"]), reverse=True)

        logger.info(f"搜索查询: '{query}', 找到 {len(results)} 个结果")
        return results[:top_k]

    def _keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """关键词搜索（备用方案）"""
        if not self.documents:
            return []

        results = []
        query_lower = query.lower()

        for doc in self.documents:
            score = 0
            content_lower = doc.page_content.lower()

            # 改进的关键词匹配
            if query_lower in content_lower:
                score = 1.0
            else:
                # 计算查询词的匹配度
                query_words = set(query_lower.split())
                content_words = set(content_lower.split())
                matches = len(query_words & content_words)
                if matches > 0:
                    score = matches / len(query_words)

            if score > 0.3:  # 降低阈值
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score * 0.8,  # 关键词检索分数略低
                    "method": "keyword"
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _call_deepseek_api(self, query: str, context: str) -> str:
        """调用DeepSeek API生成答案"""
        try:
            import httpx

            prompt = f"""你是一个车载测试领域的专家助手。请根据以下参考信息回答用户的问题。

参考信息：
{context}

用户问题：{query}

请用中文回答，保持准确和专业。如果参考信息不足以回答问题，请说明。"""

            headers = {
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个车载测试领域的专家助手。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return f"抱歉，生成答案时出错：{str(e)}"

    def query_with_sources(self, query: str, use_llm: bool = True) -> Dict[str, Any]:
        """执行查询并返回结果和来源"""

        # 1. 检索相关文档
        relevant_docs = self.search_similar(query, settings.TOP_K)

        if not relevant_docs:
            return {
                "answer": "抱歉，我没有找到相关信息来回答您的问题。请尝试使用其他关键词。",
                "sources": [],
                "context": [],
                "query": query
            }

        # 2. 构建上下文
        context = "\n\n---\n\n".join([
            f"来源: {doc['metadata'].get('source', '未知')}\n内容: {doc['content']}"
            for doc in relevant_docs
        ])

        # 3. 生成答案
        if use_llm and settings.DEEPSEEK_API_KEY:
            answer = self._call_deepseek_api(query, context)
        else:
            # 不使用LLM时的简单答案
            answer = f"我找到的相关信息如下：\n\n{context}"

        # 4. 构建来源列表
        sources = [
            {
                "content": doc["content"][:300] + "..." if len(doc["content"]) > 300 else doc["content"],
                "metadata": doc["metadata"],
                "score": doc["score"],
                "method": doc.get("method", "unknown")
            }
            for doc in relevant_docs
        ]

        return {
            "answer": answer,
            "sources": sources,
            "context": [doc["content"] for doc in relevant_docs],
            "query": query,
            "llm_used": use_llm and settings.DEEPSEEK_API_KEY is not None
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        vector_status = "disabled"
        vector_info = {}

        if self.vector_engine:
            try:
                vector_info = self.vector_engine.get_collection_info()
                vector_status = "connected" if vector_info else "error"
            except Exception as e:
                vector_status = f"error: {str(e)}"

        return {
            "status": "healthy" if self.is_initialized else "uninitialized",
            "vector_search": vector_status,
            "vector_info": vector_info,
            "document_count": len(self.documents),
            "config": {
                "top_k": settings.TOP_K,
                "chunk_size": settings.CHUNK_SIZE,
                "rerank_enabled": settings.RERANK_ENABLED,
                "cache_enabled": settings.CACHE_ENABLED,
                "qdrant_host": settings.QDRANT_HOST,
                "qdrant_port": settings.QDRANT_PORT,
                "llm_provider": settings.LLM_PROVIDER
            }
        }


# 全局实例
enhanced_rag_engine = None


def get_rag_engine(use_local: bool = False):
    """获取 RAG 引擎实例

    Args:
        use_local: 是否强制使用本地向量引擎（不尝试连接外部服务）
    """
    global enhanced_rag_engine
    if enhanced_rag_engine is None:
        if use_local:
            enhanced_rag_engine = EnhancedRAGEngine(use_vector=False)
            enhanced_rag_engine.initialize()
            # 初始化本地向量引擎
            from local_vector_store import LocalVectorStore
            enhanced_rag_engine.vector_engine = LocalVectorStore()
            enhanced_rag_engine.vector_engine.backend_type = "local_tfidf"
            logger.info("Using local TF-IDF vector engine")
        else:
            enhanced_rag_engine = EnhancedRAGEngine(use_vector=True)
            enhanced_rag_engine.initialize()
    return enhanced_rag_engine


def clear_all_cache():
    """清除所有缓存"""
    logger.info("Cache cleared")
