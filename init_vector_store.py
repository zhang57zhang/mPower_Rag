"""
初始化向量数据库并索引文档
"""
import sys
from pathlib import Path
from simple_config import settings, Document
from simple_rag_engine import EnhancedRAGEngine
import logging

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_test_documents() -> List[Document]:
    """加载测试文档"""
    knowledge_dir = settings.knowledge_base_dir

    documents = []

    # 遍历知识库目录中的所有文件
    for file_path in knowledge_dir.glob("*.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 按段落分块
            chunks = []
            paragraphs = content.split("\n\n")

            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                if len(current_chunk) + len(para) + 2 < settings.chunk_size:
                    current_chunk += "\n\n" + para if current_chunk else para
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = para

            if current_chunk:
                chunks.append(current_chunk)

            # 为每个chunk创建文档
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # 跳过太短的块
                    continue

                doc = Document(
                    page_content=chunk.strip(),
                    metadata={
                        "source": file_path.name,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)

            logger.info(f"从 {file_path.name} 加载了 {len(chunks)} 个文档块")

        except Exception as e:
            logger.error(f"加载文件 {file_path} 失败: {e}")

    logger.info(f"总共加载了 {len(documents)} 个文档块")
    return documents


def main():
    """主函数"""
    print("=" * 60)
    print("初始化向量数据库")
    print("=" * 60)

    # 1. 检查Qdrant连接
    print("\n[1/4] 检查Qdrant连接...")
    try:
        from vector_search import VectorSearchEngine
        vector_engine = VectorSearchEngine(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        print(f"✓ Qdrant连接成功: {settings.qdrant_host}:{settings.qdrant_port}")
    except Exception as e:
        print(f"✗ Qdrant连接失败: {e}")
        print("\n请确保Qdrant服务正在运行:")
        print("  Windows: qdrant.exe")
        print("  Docker: docker run -p 6333:6333 qdrant/qdrant:latest")
        return

    # 2. 获取当前集合状态
    print("\n[2/4] 检查集合状态...")
    collection_info = vector_engine.get_collection_info()
    if collection_info:
        print(f"当前集合信息:")
        print(f"  - 名称: {collection_info.get('name')}")
        print(f"  - 文档数量: {collection_info.get('points_count', 0)}")
        print(f"  - 状态: {collection_info.get('status')}")

        # 询问是否重新索引
        if collection_info.get('points_count', 0) > 0:
            response = input("\n检测到已有数据，是否重新索引？(y/n): ")
            if response.lower() != 'y':
                print("跳过文档索引")
                return

    # 3. 加载文档
    print("\n[3/4] 加载文档...")
    documents = load_test_documents()

    if not documents:
        print("✗ 没有找到文档")
        print(f"请将文档放在 {settings.knowledge_base_dir} 目录下")
        return

    print(f"✓ 加载了 {len(documents)} 个文档块")

    # 4. 索引文档
    print("\n[4/4] 索引文档到向量数据库...")
    vector_docs = []
    for i, doc in enumerate(documents):
        vector_docs.append({
            "id": f"{doc.metadata['source']}_{i}",
            "content": doc.page_content,
            "source": doc.metadata["source"],
            "metadata": doc.metadata
        })

        if (i + 1) % 10 == 0:
            print(f"  处理进度: {i+1}/{len(documents)}")

    success = vector_engine.add_documents(vector_docs)
    if success:
        print(f"✓ 成功索引 {len(vector_docs)} 个文档块")
    else:
        print("✗ 文档索引失败")
        return

    # 5. 验证索引
    print("\n验证索引...")
    new_info = vector_engine.get_collection_info()
    print(f"最终集合信息:")
    print(f"  - 名称: {new_info.get('name')}")
    print(f"  - 文档数量: {new_info.get('points_count', 0)}")
    print(f"  - 向量数量: {new_info.get('vectors_count', 0)}")

    # 6. 测试检索
    print("\n测试检索...")
    test_queries = ["蓝牙", "ECU", "测试", "诊断"]
    for query in test_queries:
        results = vector_engine.search(query, top_k=3)
        print(f"\n查询: '{query}'")
        if results:
            for i, result in enumerate(results):
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"  {i+1}. [{result['score']:.3f}] {content_preview}")
        else:
            print("  未找到结果")

    print("\n" + "=" * 60)
    print("初始化完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
