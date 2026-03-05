"""
启动时自动加载文档
支持多格式：txt/md/docx/xlsx/pdf
"""
import sys
from pathlib import Path
from simple_config import settings, Document
from simple_rag_engine import get_rag_engine
from document_parser import DocumentParser

def load_knowledge_on_startup():
    """启动时加载知识库（支持多格式）"""

    # 获取RAG引擎实例
    rag_engine = get_rag_engine()

    # 知识库目录
    knowledge_base_dir = settings.knowledge_base_dir

    print("启动时加载知识库文档...")

    # 支持的文件格式
    supported_extensions = ['.txt', '.md', '.docx', '.xlsx', '.pdf']

    # 扫描所有支持的文件
    documents = []
    for ext in supported_extensions:
        for file_path in knowledge_base_dir.glob(f"*{ext}"):
            print(f"加载文件: {file_path.name}")

            try:
                # 读取文件内容
                with open(file_path, 'rb') as f:
                    content = f.read()

                # 解析文档
                text, metadata = DocumentParser.parse(content, file_path.name)

                # 创建文档对象
                document = Document(
                    page_content=text,
                    metadata=metadata
                )

                documents.append(document)
                print(f"  - 加载成功: {len(text)} 字符 (格式: {metadata['format']})")

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