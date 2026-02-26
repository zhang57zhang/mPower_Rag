"""
缓存增强的 RAG 引擎
支持查询缓存、向量检索缓存、LLM 响应缓存
"""
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.schema import LLMResult
import logging

from .vector_store import VectorStoreManager
from .embeddings import get_embeddings
from .conversation import ConversationManager
from .rerank import CrossEncoderReranker
from .utils.cache import get_cache, cache_decorator, CACHE_PREFIX_QUERY, CACHE_PREFIX_RETRIEVAL, CACHE_PREFIX_LLM

logger = logging.getLogger(__name__)


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器"""

    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """处理新生成的 token"""
        self.tokens.append(token)
        logger.debug(f"New token: {token}")

    def get_text(self) -> str:
        """获取生成的完整文本"""
        return "".join(self.tokens)

    def clear(self) -> None:
        """清空 tokens"""
        self.tokens = []


class CachedRAGEngine:
    """缓存增强的 RAG 引擎"""

    def __init__(
        self,
        vector_store: VectorStoreManager,
        conversation_manager: Optional[ConversationManager] = None,
        llm_provider: str = "deepseek",
        llm_model: str = "deepseek-chat",
        llm_api_key: Optional[str] = None,
        llm_base_url: str = "https://api.deepseek.com",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        use_rerank: bool = False,
        rerank_method: str = "cross_encoder",
        rerank_model: str = "BAAI/bge-reranker-base",
        enable_cache: bool = False,
        cache_config: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化 RAG 引擎（带缓存）

        Args:
            vector_store: 向量存储
            conversation_manager: 对话管理器（可选）
            llm_provider: LLM 提供商
            llm_model: 模型名称
            llm_api_key: API 密钥
            llm_base_url: API 基础 URL
            temperature: 温度参数
            max_tokens: 最大 token 数
            use_rerank: 是否使用重排序
            rerank_method: 重排序方法
            rerank_model: 重排序模型名称
            enable_cache: 是否启用缓存
            cache_config: 缓存配置
        """
        self.vector_store = vector_store
        self.conversation_manager = conversation_manager
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 重排序配置
        self.use_rerank = use_rerank
        self.rerank_method = rerank_method
        self.rerank_model = rerank_model

        # 缓存配置
        self.enable_cache = enable_cache
        self.cache_config = cache_config or {}

        # 初始化缓存
        self.cache = None
        if self.enable_cache:
            self.cache = get_cache(self.cache_config)
            if self.cache is not None:
                logger.info("缓存已启用")
            else:
                logger.warning("缓存初始化失败，缓存功能未启用")

        # 初始化重排序器
        self.reranker = None
        if self.use_rerank and self.rerank_method == "cross_encoder":
            try:
                self.reranker = CrossEncoderReranker(model_name=rerank_model)
                logger.info(f"重排序器已初始化: {rerank_model}")
            except Exception as e:
                logger.warning(f"重排序器初始化失败: {e}，将禁用重排序")
                self.use_rerank = False

        # 初始化 LLM
        self.llm = ChatOpenAI(
            model_name=llm_model,
            openai_api_key=llm_api_key,
            openai_api_base=llm_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 创建问答链
        self.qa_chain = self._create_qa_chain()

    def _create_qa_chain(self):
        """创建问答链"""
        prompt_template = """你是一个车载测试专家助手。请根据以下检索到的知识库内容，回答用户的问题。

知识库内容：
{context}

用户问题：
{question}

要求：
1. 基于知识库内容回答，不要编造信息
2. 如果知识库中没有相关信息，明确告知用户
3. 回答要专业、准确、有针对性
4. 可以分点说明，便于阅读
5. 如需引用具体测试标准或规范，请标明来源

回答："""

        prompt = ChatPromptTemplate.from_template(prompt_template)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.vector_store.as_retriever(
                search_kwargs={"k": 5}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        return qa_chain

    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """
        执行查询（带缓存）

        Args:
            question: 用户问题
            **kwargs: 其他参数
                - conversation_id: 对话 ID（可选）
                - use_history: 是否使用对话历史（默认 False）
                - skip_cache: 是否跳过缓存（默认 False）

        Returns:
            包含答案和源文档的字典
        """
        skip_cache = kwargs.get("skip_cache", False)

        try:
            conversation_id = kwargs.get("conversation_id")
            use_history = kwargs.get("use_history", False)

            # 尝试从缓存获取查询结果
            if not skip_cache and self.enable_cache and self.cache:
                cache_key = {
                    "question": question,
                    "conversation_id": conversation_id,
                    "use_history": use_history,
                }

                cached_result = self.cache.get(CACHE_PREFIX_QUERY, cache_key)
                if cached_result is not None:
                    logger.info(f"查询缓存命中: {question[:50]}...")
                    return cached_result

            # 如果缓存未命中，执行查询
            logger.info(f"查询缓存未命中，执行查询: {question[:50]}...")

            # 如果使用对话历史且有对话 ID，添加历史上下文
            if use_history and conversation_id and self.conversation_manager:
                try:
                    history = self.conversation_manager.get_history(conversation_id)
                    context_str = self._format_history_context(history)
                    prompt_with_history = f"以下是对话历史：\n{context_str}\n\n当前问题：{question}"
                    result = self.qa_chain.invoke({"query": prompt_with_history})

                    # 保存用户消息和助手回复到对话历史
                    self.conversation_manager.add_message(
                        conversation_id=conversation_id,
                        role="user",
                        content=question,
                    )
                    self.conversation_manager.add_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=result["result"],
                        metadata={"sources": len(result["source_documents"])}
                    )
                except Exception as e:
                    logger.warning(f"处理对话历史失败，使用单轮模式: {e}")
                    result = self.qa_chain.invoke({"query": question})
            else:
                result = self.qa_chain.invoke({"query": question})

            # 构建响应
            response = {
                "answer": result["result"],
                "source_documents": result["source_documents"],
                "question": question,
                "conversation_id": conversation_id,
                "cached": False,
            }

            # 将结果存入缓存
            if not skip_cache and self.enable_cache and self.cache:
                self.cache.set(CACHE_PREFIX_QUERY, cache_key, response)

            return response

        except Exception as e:
            logger.error(f"查询失败: {e}")
            return {
                "answer": f"查询失败：{str(e)}",
                "source_documents": [],
                "question": question,
                "conversation_id": kwargs.get("conversation_id"),
                "cached": False,
            }

    def _format_history_context(self, history: List[Dict[str, str]]) -> str:
        """
        格式化对话历史为上下文字符串

        Args:
            history: 对话历史列表

        Returns:
            格式化的上下文字符串
        """
        if not history:
            return ""

        context_parts = []
        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)

    def query_with_sources(
        self, question: str, top_k: int = 5, use_rerank: bool = None, skip_cache: bool = False
    ) -> Dict[str, Any]:
        """
        执行查询并返回源文档详情（带缓存）

        Args:
            question: 用户问题
            top_k: 返回的文档数量
            use_rerank: 是否使用重排序（None 表示使用默认配置）
            skip_cache: 是否跳过缓存

        Returns:
            包含答案和源文档详情的字典
        """
        should_rerank = use_rerank if use_rerank is not None else self.use_rerank

        # 缓存键
        cache_key = {
            "question": question,
            "top_k": top_k,
            "use_rerank": should_rerank,
        }

        # 尝试从缓存获取检索结果
        cached_docs = None
        if not skip_cache and self.enable_cache and self.cache:
            cached_docs = self.cache.get(CACHE_PREFIX_RETRIEVAL, cache_key)
            if cached_docs is not None:
                logger.info(f"检索缓存命中: {question[:50]}...")

        # 检索相关文档
        if cached_docs is None:
            retrieval_k = top_k * 2 if should_rerank else top_k
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=question, k=retrieval_k
            )

            # 如果启用了重排序，执行重排序
            if should_rerank and self.reranker:
                docs_with_scores = self._rerank_documents(
                    documents=[doc for doc, score in docs_with_scores],
                    scores=[score for doc, score in docs_with_scores],
                    query=question,
                    top_k=top_k,
                )

            # 限制返回的文档数量
            docs_with_scores = docs_with_scores[:top_k]

            # 将检索结果存入缓存
            if not skip_cache and self.enable_cache and self.cache:
                self.cache.set(CACHE_PREFIX_RETRIEVAL, cache_key, docs_with_scores)
        else:
            docs_with_scores = cached_docs

        # 提取文档和分数
        documents = [doc for doc, score in docs_with_scores]
        scores = [score for doc, score in docs_with_scores]

        # 执行查询
        result = self.query(question, skip_cache=skip_cache)

        # 添加文档详情
        result["source_details"] = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
            for doc, score in docs_with_scores
        ]

        # 添加重排序信息
        result["reranked"] = should_rerank
        result["rerank_method"] = self.rerank_method if should_rerank else None
        result["retrieval_cached"] = cached_docs is not None

        return result

    def _rerank_documents(
        self,
        documents: List[Document],
        scores: List[float],
        query: str,
        top_k: int = 5,
    ) -> List[tuple]:
        """
        重排序文档

        Args:
            documents: 文档列表
            scores: 原始相似度分数
            query: 查询问题
            top_k: 返回的文档数量

        Returns:
            重排序后的 (文档, 分数) 元组列表
        """
        if not self.reranker:
            return list(zip(documents, scores))

        try:
            # 提取文档文本
            texts = [doc.page_content for doc in documents]

            # 执行重排序
            reranked_scores = self.reranker.rerank(
                query=query,
                documents=texts,
            )

            # 合并结果
            reranked_docs = [
                (documents[i], reranked_scores[i])
                for i in range(len(documents))
            ]

            # 按重排序分数排序（分数越高越好）
            reranked_docs.sort(key=lambda x: x[1], reverse=True)

            logger.info(f"重排序完成，返回前 {top_k} 个文档")

            return reranked_docs[:top_k]

        except Exception as e:
            logger.error(f"重排序失败: {e}，使用原始结果")
            return list(zip(documents, scores))

    def stream_query(self, question: str) -> Iterator[str]:
        """
        流式查询

        Args:
            question: 用户问题

        Yields:
            生成的文本片段
        """
        callback_handler = StreamingCallbackHandler()

        # 创建带回调的 LLM
        llm_with_callback = ChatOpenAI(
            model_name=self.llm_model,
            openai_api_key=self.llm.openai_api_key,
            openai_api_base=self.llm.openai_api_base,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=True,
            callbacks=[callback_handler],
        )

        # 使用流式 LLM 创建链
        # 这里简化实现，实际需要更复杂的流式处理
        try:
            result = llm_with_callback.predict(question)
            yield result
        except Exception as e:
            logger.error(f"流式查询失败: {e}")
            yield f"查询失败：{str(e)}"

    def add_knowledge(self, documents: List[Document]) -> List[str]:
        """
        添加知识到向量库

        Args:
            documents: 文档列表

        Returns:
            添加的文档 ID 列表
        """
        try:
            ids = self.vector_store.add_documents(documents)
            logger.info(f"成功添加 {len(documents)} 个文档到知识库")
            return ids
        except Exception as e:
            logger.error(f"添加知识失败: {e}")
            return []

    def clear_cache(self, prefix: str = None) -> bool:
        """
        清空缓存

        Args:
            prefix: 缓存前缀（None 表示清空所有）

        Returns:
            是否清空成功
        """
        if not self.enable_cache or not self.cache:
            return False

        try:
            if prefix:
                return self.cache.clear_prefix(prefix) > 0
            else:
                # 清空所有缓存
                total = 0
                for cache_prefix in [CACHE_PREFIX_QUERY, CACHE_PREFIX_RETRIEVAL, CACHE_PREFIX_LLM]:
                    total += self.cache.clear_prefix(cache_prefix)

                logger.info(f"已清空所有缓存: {total} 个键")
                return total > 0

        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计

        Returns:
            缓存统计信息
        """
        if not self.enable_cache or not self.cache:
            return {
                "enabled": False,
                "total_keys": 0,
                "connected": False,
            }

        return self.cache.get_stats()


# 全局 RAG 引擎实例
_cached_rag_engine = None


def get_cached_rag_engine(
    vector_store: VectorStoreManager,
    conversation_manager: Optional[ConversationManager] = None,
    llm_provider: str = "deepseek",
    llm_model: str = "deepseek-chat",
    llm_api_key: Optional[str] = None,
    llm_base_url: str = "https://api.deepseek.com",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    use_rerank: bool = False,
    rerank_method: str = "cross_encoder",
    rerank_model: str = "BAAI/bge-reranker-base",
    enable_cache: bool = False,
    cache_config: Optional[Dict[str, Any]] = None,
) -> CachedRAGEngine:
    """获取缓存增强的 RAG 引擎（单例）"""
    global _cached_rag_engine
    if _cached_rag_engine is None:
        _cached_rag_engine = CachedRAGEngine(
            vector_store=vector_store,
            conversation_manager=conversation_manager,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            use_rerank=use_rerank,
            rerank_method=rerank_method,
            rerank_model=rerank_model,
            enable_cache=enable_cache,
            cache_config=cache_config,
        )
    return _cached_rag_engine
