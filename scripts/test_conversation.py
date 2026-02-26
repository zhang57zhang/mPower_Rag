"""
对话功能测试脚本
测试对话管理的各项功能
"""
import requests
import json
from typing import Dict, Any

# API 基础 URL
API_BASE_URL = "http://localhost:8000/api/v1"


def print_json(data: Dict[str, Any], title: str = ""):
    """打印 JSON 格式的数据"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def test_create_conversation():
    """测试创建对话"""
    print("\n" + "="*60)
    print("测试 1: 创建新对话")
    print("="*60)

    response = requests.post(
        f"{API_BASE_URL}/conversations",
        json={"metadata": {"test": True}},
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "创建对话响应")
        return result["conversation_id"]
    else:
        print(f"❌ 创建对话失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None


def test_list_conversations():
    """测试列出对话"""
    print("\n" + "="*60)
    print("测试 2: 列出所有对话")
    print("="*60)

    response = requests.get(
        f"{API_BASE_URL}/conversations",
        params={"limit": 10},
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "对话列表")
        return result["conversations"]
    else:
        print(f"❌ 列出对话失败: {response.status_code}")
        return []


def test_get_conversation(conversation_id: str):
    """测试获取对话详情"""
    print("\n" + "="*60)
    print(f"测试 3: 获取对话详情 {conversation_id}")
    print("="*60)

    response = requests.get(
        f"{API_BASE_URL}/conversations/{conversation_id}",
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "对话详情")
        return result
    else:
        print(f"❌ 获取对话失败: {response.status_code}")
        return None


def test_send_message(conversation_id: str, question: str):
    """测试发送消息"""
    print("\n" + "="*60)
    print(f"测试 4: 发送消息到对话 {conversation_id}")
    print("="*60)

    response = requests.post(
        f"{API_BASE_URL}/conversations/{conversation_id}/messages",
        json={
            "question": question,
            "top_k": 5,
            "use_history": True,
        },
        timeout=60,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "发送消息响应")
        return result
    else:
        print(f"❌ 发送消息失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None


def test_multi_turn_conversation(conversation_id: str):
    """测试多轮对话"""
    print("\n" + "="*60)
    print("测试 5: 多轮对话")
    print("="*60)

    questions = [
        "什么是车载测试？",
        "测试流程有哪些步骤？",
        "测试需要注意什么？",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n第 {i} 轮:")
        print(f"问题: {question}")

        result = test_send_message(conversation_id, question)

        if result:
            print(f"答案: {result['answer'][:200]}...")
            print(f"参考文档数量: {len(result.get('source_documents', []))}")
        else:
            print("❌ 获取答案失败")


def test_delete_conversation(conversation_id: str):
    """测试删除对话"""
    print("\n" + "="*60)
    print(f"测试 6: 删除对话 {conversation_id}")
    print("="*60)

    response = requests.delete(
        f"{API_BASE_URL}/conversations/{conversation_id}",
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "删除对话响应")
        return True
    else:
        print(f"❌ 删除对话失败: {response.status_code}")
        return False


def main():
    """主测试函数"""
    print("\n" + "#"*60)
    print("#  mPower_Rag 对话功能测试")
    print("#"*60)

    # 测试 1: 创建对话
    conversation_id = test_create_conversation()

    if not conversation_id:
        print("\n❌ 无法创建对话，终止测试")
        return

    # 测试 2: 列出对话
    test_list_conversations()

    # 测试 3: 获取对话详情
    test_get_conversation(conversation_id)

    # 测试 4: 发送消息（单轮）
    test_send_message(conversation_id, "你好，车载测试是什么？")

    # 测试 5: 多轮对话
    test_multi_turn_conversation(conversation_id)

    # 再次获取对话详情，查看消息历史
    test_get_conversation(conversation_id)

    # 测试 6: 删除对话（可选）
    print("\n是否要删除测试对话？(y/n): ", end="")
    choice = input().strip().lower()

    if choice == 'y':
        test_delete_conversation(conversation_id)

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
