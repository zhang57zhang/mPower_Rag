"""
调试RAG引擎功能
"""
import sys
from simple_config import settings, Document
from simple_rag_engine import get_rag_engine

def debug_rag():
    """调试RAG引擎"""
    
    print("调试RAG引擎...")
    
    # 获取RAG引擎实例
    rag_engine = get_rag_engine()
    
    # 检查引擎状态
    print(f"\n引擎状态: {rag_engine.health_check()}")
    print(f"文档数量: {len(rag_engine.documents)}")
    
    # 手动添加一个测试文档
    test_doc = Document(
        page_content="这是一个测试文档，关于车载蓝牙测试。包含连接稳定性测试方法。",
        metadata={"filename": "test_doc.txt", "type": "test"}
    )
    
    print(f"\n添加测试文档: {test_doc}")
    rag_engine.add_documents([test_doc])
    
    print(f"添加后文档数量: {len(rag_engine.documents)}")
    
    # 测试搜索
    test_queries = [
        "蓝牙测试",
        "ECU诊断",
        "连接稳定性",
        "车载系统"
    ]
    
    for query in test_queries:
        print(f"\n搜索: '{query}'")
        results = rag_engine.search_similar(query, top_k=3)
        print(f"结果数量: {len(results)}")
        
        for i, doc in enumerate(results, 1):
            score = getattr(doc, 'score', 0)
            preview = doc.page_content[:100] + "..."
            print(f"  {i}. [{score:.2f}] {preview}")
    
    # 测试完整查询
    print(f"\n测试完整查询:")
    result = rag_engine.query_with_sources("蓝牙测试方法")
    print(f"答案: {result['answer']}")
    print(f"来源数量: {len(result['sources'])}")
    print(f"上下文数量: {len(result['context'])}")

if __name__ == "__main__":
    debug_rag()