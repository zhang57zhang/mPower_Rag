"""
启动时自动加载文档
"""
import sys
from pathlib import Path
from simple_config import settings, Document
from simple_rag_engine import get_rag_engine

def load_knowledge_on_startup():
    """启动时加载知识库"""
    
    # 获取RAG引擎实例
    rag_engine = get_rag_engine()
    
    # 知识库目录
    knowledge_base_dir = settings.knowledge_base_dir
    
    print("启动时加载知识库文档...")
    
    # 扫描所有文本文件
    documents = []
    for file_path in knowledge_base_dir.glob("*.txt"):
        print(f"加载文件: {file_path.name}")
        
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
            print(f"  - 加载成功: {len(content)} 字符")
            
        except Exception as e:
            print(f"  - 加载失败: {e}")
    
    # 添加文档到RAG引擎
    if documents:
        print(f"\n添加 {len(documents)} 个文档到RAG引擎...")
        rag_engine.add_documents(documents)
        print("知识库加载完成！")
        return True
    else:
        print("未找到任何文档")
        return False

if __name__ == "__main__":
    load_knowledge_on_startup()