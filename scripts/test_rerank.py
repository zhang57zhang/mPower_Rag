"""
重排序功能测试脚本
测试重排序器的各项功能
"""
import requests
import json
from typing import Dict, Any
import time

# API 基础 URL
API_BASE_URL = "http://localhost:8000/api/v1"


def print_json(data: Dict[str, Any], title: str = ""):
    """打印 JSON 格式的数据"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def test_rerank_chat():
    """测试带重排序的问答"""
    print("\n" + "="*60)
    print("测试 1: 带重排序的问答")
    print("="*60)

    questions = [
        "什么是车载测试？",
        "车载 CAN 总线测试的标准流程是什么？",
        "如何诊断车载电源系统的故障？",
    ]

    for question in questions:
        print(f"\n问题: {question}")

        # 不使用重排序
        print("\n不使用重排序:")
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": question, "top_k": 3, "use_rerank": False},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"答案: {result['answer'][:100]}...")
            print(f"源文档数量: {len(result.get('source_documents', []))}")
            if result.get('metadata'):
                print(f"元数据: {result['metadata']}")
        else:
            print(f"❌ 失败: {response.status_code}")

        # 使用重排序
        print("\n使用重排序:")
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": question, "top_k": 3, "use_rerank": True},
            timeout=60,  # 重排序可能需要更长时间
        )

        if response.status_code == 200:
            result = response.json()
            print(f"答案: {result['answer'][:100]}...")
            print(f"源文档数量: {len(result.get('source_documents', []))}")
            if result.get('metadata'):
                print(f"元数据: {result['metadata']}")
        else:
            print(f"❌ 失败: {response.status_code}")


def test_rerank_conversation():
    """测试带重排序的对话"""
    print("\n" + "="*60)
    print("测试 2: 带重排序的多轮对话")
    print("="*60)

    # 创建对话
    print("\n创建对话...")
    response = requests.post(
        f"{API_BASE_URL}/conversations",
        json={"metadata": {"test": "rerank"}},
        timeout=10,
    )

    if response.status_code != 200:
        print(f"❌ 创建对话失败: {response.status_code}")
        return

    conversation_id = response.json()["conversation_id"]
    print(f"✅ 对话创建成功: {conversation_id}")

    # 发送消息（不使用重排序）
    print("\n第 1 轮（不使用重排序）:")
    response = requests.post(
        f"{API_BASE_URL}/conversations/{conversation_id}/messages",
        json={
            "question": "什么是车载测试？",
            "top_k": 3,
            "use_history": False,
            "use_rerank": False,
        },
        timeout=30,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"答案: {result['answer'][:100]}...")
    else:
        print(f"❌ 失败: {response.status_code}")

    # 发送消息（使用重排序）
    print("\n第 2 轮（使用重排序）:")
    response = requests.post(
        f"{API_BASE_URL}/conversations/{conversation_id}/messages",
        json={
            "question": "测试流程有哪些步骤？",
            "top_k": 3,
            "use_history": True,
            "use_rerank": True,
        },
        timeout=60,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"答案: {result['answer'][:100]}...")
        print(f"源文档数量: {len(result.get('source_documents', []))}")
    else:
        print(f"❌ 失败: {response.status_code}")

    # 删除对话
    print("\n删除对话...")
    requests.delete(
        f"{API_BASE_URL}/conversations/{conversation_id}",
        timeout=10,
    )


def test_rerank_performance():
    """测试重排序性能"""
    print("\n" + "="*60)
    print("测试 3: 重排序性能")
    print("="*60)

    question = "如何测试车载蓝牙模块的连接稳定性？"

    # 测试不使用重排序
    print("\n不使用重排序:")
    start_time = time.time()
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={"question": question, "top_k": 5, "use_rerank": False},
        timeout=30,
    )
    without_rerank_time = time.time() - start_time

    if response.status_code == 200:
        print(f"✅ 响应时间: {without_rerank_time:.2f} 秒")
        result = response.json()
        print(f"答案长度: {len(result['answer'])} 字符")
    else:
        print(f"❌ 失败: {response.status_code}")

    # 测试使用重排序
    print("\n使用重排序:")
    start_time = time.time()
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={"question": question, "top_k": 5, "use_rerank": True},
        timeout=60,
    )
    with_rerank_time = time.time() - start_time

    if response.status_code == 200:
        print(f"✅ 响应时间: {with_rerank_time:.2f} 秒")
        result = response.json()
        print(f"答案长度: {len(result['answer'])} 字符")
        print(f"性能开销: {(with_rerank_time - without_rerank_time):.2f} 秒")
        print(f"性能开销: {((with_rerank_time - without_rerank_time) / without_rerank_time * 100):.1f}%")
    else:
        print(f"❌ 失败: {response.status_code}")


def main():
    """主测试函数"""
    print("\n" + "#"*60)
    print("#  mPower_Rag 重排序功能测试")
    print("#"*60)

    try:
        # 测试带重排序的问答
        test_rerank_chat()

        # 测试带重排序的对话
        test_rerank_conversation()

        # 测试重排序性能
        test_rerank_performance()

    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()
