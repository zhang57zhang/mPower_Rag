"""
测试新功能
测试多格式文档解析、删除和外部API集成
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from document_parser import DocumentParser, is_format_supported, get_supported_formats
from external_api import ExternalAPIClient
from simple_rag_engine import get_rag_engine
from simple_config import Document


def test_document_parser():
    """测试文档解析器"""
    print("\n=== 测试文档解析器 ===")

    # 测试TXT
    print("\n1. 测试TXT格式:")
    txt_content = b"This is a test document.\nIt has multiple lines."
    text, metadata = DocumentParser.parse(txt_content, "test.txt")
    print(f"  解析成功: {len(text)} 字符")
    print(f"  元数据: {metadata}")

    # 测试Markdown
    print("\n2. 测试Markdown格式:")
    md_content = b"# Title\n\nThis is **bold** text.\n\n- Item 1\n- Item 2"
    text, metadata = DocumentParser.parse(md_content, "test.md")
    print(f"  解析成功: {len(text)} 字符")
    print(f"  元数据: {metadata}")

    # 测试DOCX（如果有测试文件）
    print("\n3. 测试DOCX格式:")
    docx_path = Path("knowledge_base/test.docx")
    if docx_path.exists():
        with open(docx_path, 'rb') as f:
            docx_content = f.read()
        text, metadata = DocumentParser.parse(docx_content, "test.docx")
        print(f"  解析成功: {len(text)} 字符")
        print(f"  元数据: {metadata}")
    else:
        print("  跳过：没有测试文件")

    # 测试PDF（如果有测试文件）
    print("\n4. 测试PDF格式:")
    pdf_path = Path("knowledge_base/test.pdf")
    if pdf_path.exists():
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        text, metadata = DocumentParser.parse(pdf_content, "test.pdf")
        print(f"  解析成功: {len(text)} 字符")
        print(f"  元数据: {metadata}")
    else:
        print("  跳过：没有测试文件")

    # 测试不支持的格式
    print("\n5. 测试不支持的格式:")
    print(f"  .txt 支持: {is_format_supported('test.txt')}")
    print(f"  .xyz 支持: {is_format_supported('test.xyz')}")

    # 显示所有支持的格式
    print("\n6. 支持的格式:")
    for ext, mime in get_supported_formats().items():
        print(f"  {ext}: {mime}")


def test_document_deletion():
    """测试文档删除功能"""
    print("\n=== 测试文档删除功能 ===")

    # 获取RAG引擎
    engine = get_rag_engine(use_local=True)

    # 添加测试文档
    print("\n1. 添加测试文档:")
    doc1 = Document(
        page_content="这是第一个测试文档",
        metadata={"filename": "test1.txt", "index": 1}
    )
    doc2 = Document(
        page_content="这是第二个测试文档",
        metadata={"filename": "test2.txt", "index": 2}
    )
    engine.add_documents([doc1, doc2])
    print(f"  添加了2个文档，当前文档数: {len(engine.documents)}")

    # 列出所有文档
    print("\n2. 列出所有文档:")
    docs = engine.list_documents()
    for doc in docs:
        print(f"  ID: {doc['id']}, 文件名: {doc['metadata'].get('filename')}")

    # 删除单个文档
    if docs:
        print(f"\n3. 删除文档: {docs[0]['id']}")
        success = engine.remove_document(docs[0]['id'])
        print(f"  删除成功: {success}")
        print(f"  剩余文档数: {len(engine.documents)}")

    # 批量删除
    print("\n4. 批量删除:")
    remaining_docs = engine.list_documents()
    if remaining_docs:
        doc_ids = [doc['id'] for doc in remaining_docs]
        results = engine.remove_documents_batch(doc_ids)
        print(f"  删除结果: {results}")
        print(f"  剩余文档数: {len(engine.documents)}")


def test_external_api():
    """测试外部API集成"""
    print("\n=== 测试外部API集成 ===")

    # 测试健康检查
    print("\n1. 测试健康检查:")
    client = ExternalAPIClient()
    result = client.health_check("https://httpbin.org/status/200")
    print(f"  结果: {result}")

    # 测试获取文档
    print("\n2. 测试获取文档:")
    result = client.fetch_document("https://httpbin.org/json")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  内容长度: {len(result['content'])} 字符")
        print(f"  元数据: {result['metadata']}")
    else:
        print(f"  错误: {result.get('error')}")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("mPower_Rag 新功能测试")
    print("=" * 60)

    try:
        test_document_parser()
        test_document_deletion()
        test_external_api()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
