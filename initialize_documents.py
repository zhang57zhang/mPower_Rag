"""
初始化文档到知识库
"""
import sys
from pathlib import Path
from simple_config import settings, Document
from simple_rag_engine import get_rag_engine

def initialize_knowledge_base():
    """初始化知识库"""
    
    # 获取RAG引擎实例
    rag_engine = get_rag_engine()
    
    # 知识库目录
    knowledge_base_dir = settings.knowledge_base_dir
    
    print("正在初始化知识库...")
    print(f"知识库目录: {knowledge_base_dir}")
    
    # 扫描所有文本文件
    documents = []
    for file_path in knowledge_base_dir.glob("*.txt"):
        print(f"读取文件: {file_path.name}")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建文档对象
            document = Document(
                page_content=content,
                metadata={
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "size": len(content)
                }
            )
            
            documents.append(document)
            print(f"  - 文档大小: {len(content)} 字符")
            
        except Exception as e:
            print(f"  - 读取文件失败: {e}")
    
    # 添加文档到RAG引擎
    if documents:
        print(f"\n添加 {len(documents)} 个文档到RAG引擎...")
        rag_engine.add_documents(documents)
        
        # 测试搜索
        print("\n测试搜索功能...")
        test_queries = [
            "蓝牙测试",
            "ECU诊断", 
            "发动机性能",
            "CAN总线"
        ]
        
        for query in test_queries:
            print(f"\n搜索 '{query}'...")
            results = rag_engine.search_similar(query, top_k=3)
            
            if results:
                print(f"  找到 {len(results)} 个相关文档:")
                for i, doc in enumerate(results, 1):
                    score = getattr(doc, 'score', 0)
                    preview = doc.page_content[:100] + "..."
                    print(f"    {i}. [{score:.2f}] {preview}")
            else:
                print(f"  未找到相关文档")
    
    print("\n知识库初始化完成！")
    
    # 显示统计信息
    health = rag_engine.health_check()
    print(f"\n引擎状态: {health['status']}")
    print(f"文档数量: {health['document_count']}")

if __name__ == "__main__":
    initialize_knowledge_base()