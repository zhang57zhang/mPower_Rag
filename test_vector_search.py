"""
快速测试脚本 - 验证向量检索功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from simple_config import settings
from simple_rag_engine import EnhancedRAGEngine

def test_vector_search():
    """测试向量检索功能"""
    print("=" * 60)
    print("测试向量检索功能")
    print("=" * 60)

    # 1. 初始化RAG引擎
    print("\n[1/4] 初始化RAG引擎...")
    engine = EnhancedRAGEngine(use_vector=True)
    success = engine.initialize()

    if not success:
        print("✗ RAG引擎初始化失败")
        return

    print("✓ RAG引擎初始化成功")

    # 2. 检查向量引擎类型
    print("\n[2/4] 检查向量引擎类型...")
    if engine.vector_engine:
        backend_type = engine.vector_engine.backend_type
        print(f"向量引擎类型: {backend_type}")

        if backend_type == "qdrant":
            print("✓ 使用Qdrant向量数据库")
        else:
            print("✓ 使用内存向量存储（Qdrant不可用）")
    else:
        print("✗ 向量引擎未初始化")
        return

    # 3. 加载测试文档
    print("\n[3/4] 加载测试文档...")

    # 创建测试文档
    from simple_config import Document
    test_documents = [
        Document(
            "蓝牙测试是车载通信测试的重要组成部分。测试步骤包括设备发现、配对、连接验证和数据传输测试。",
            metadata={"source": "bluetooth_test.txt"}
        ),
        Document(
            "ECU诊断是通过OBD接口读取车辆故障码和实时数据。常用协议包括ISO 15765、KWP2000和UDS。",
            metadata={"source": "ecu_diagnosis.txt"}
        ),
        Document(
            "CAN总线测试需要验证数据帧的完整性、时序和负载率。工具包括Vector CANoe和CANalyzer。",
            metadata={"source": "can_bus_test.txt"}
        ),
        Document(
            "车载软件测试包括单元测试、集成测试和系统测试。自动化测试框架可以显著提高测试效率。",
            metadata={"source": "software_test.txt"}
        )
    ]

    print(f"添加 {len(test_documents)} 个测试文档...")
    engine.add_documents(test_documents)
    print("✓ 测试文档添加成功")

    # 4. 测试检索
    print("\n[4/4] 测试检索功能...")
    test_queries = [
        "蓝牙",
        "ECU诊断",
        "CAN总线",
        "软件测试",
        "测试工具"
    ]

    for query in test_queries:
        results = engine.search_similar(query, top_k=2)

        print(f"\n查询: '{query}'")
        if results:
            for i, result in enumerate(results):
                content_preview = result['content'][:80] + "..." if len(result['content']) > 80 else result['content']
                method_mark = "🔍" if result.get("method") == "vector" else "📝"
                print(f"  {i+1}. {method_mark} [{result['score']:.3f}] {content_preview}")
        else:
            print("  未找到结果")

    # 5. 测试完整问答
    print("\n" + "=" * 60)
    print("测试完整问答（DeepSeek）")
    print("=" * 60)

    test_question = "如何进行蓝牙测试？"
    print(f"\n问题: {test_question}")

    response = engine.query_with_sources(test_question, use_llm=True)

    print(f"\n答案:\n{response['answer']}")

    print("\n来源:")
    for i, source in enumerate(response['sources'][:2], 1):
        print(f"{i}. [{source['score']:.3f}] {source['content'][:60]}...")

    # 6. 健康检查
    print("\n" + "=" * 60)
    print("健康检查")
    print("=" * 60)

    health = engine.health_check()
    print(f"状态: {health['status']}")
    print(f"向量检索: {health['vector_search']}")
    print(f"文档数量: {health['document_count']}")
    if health.get('vector_info'):
        print(f"向量信息: {health['vector_info']}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_vector_search()
