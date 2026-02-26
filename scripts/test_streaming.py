"""
流式输出测试脚本
测试 SSE 流式响应功能
"""
import requests
import json
import time
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


def test_stream_chat():
    """测试流式聊天"""
    print("\n" + "="*60)
    print("测试 1: 流式聊天")
    print("="*60)

    questions = [
        "什么是车载测试？",
        "车载 CAN 总线测试的标准流程是什么？",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)

        response = requests.post(
            f"{API_BASE_URL}/chat/stream",
            json={
                "question": question,
                "conversation_id": None,
                "use_history": False,
                "use_rerank": False,
                "top_k": 3,
            },
            timeout=60,
            stream=True,  # 重要：启用流式响应
        )

        print("响应类型:")
        print(f"  - Headers: {response.headers.get('content-type')}")

        if response.status_code == 200:
            print("\n流式响应:")
            
            try:
                # 解析 SSE 流
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()  # 移除 "data: " 前缀
                        
                        # 移除可能的空字符串
                        if not data_str:
                            continue
                        
                        try:
                            chunk = json.loads(data_str)
                            
                            # 显示不同类型的 chunk
                            chunk_type = chunk.get("type", "unknown")
                            
                            if chunk_type == "question":
                                print(f"\n[问题] {chunk.get('content', '')}")
                            elif chunk_type == "content":
                                print(f"{chunk.get('content', '')}", end="", flush=True)
                            elif chunk_type == "done":
                                print(f"\n[完成]")
                                if chunk.get("source_documents"):
                                    print(f"  - 源文档数量: {len(chunk.get('source_documents', []))}")
                                if chunk.get("metadata"):
                                    print(f"  - 重排序: {chunk['metadata'].get('reranked', False)}")
                            elif chunk_type == "error":
                                print(f"\n[错误] {chunk.get('content', '')}")
                            
                        except json.JSONDecodeError as e:
                            print(f"\n[解析错误] {data_str}")
                            print(f"  错误: {e}")
                    
                    elif line.strip():  # 非空行
                        print(f"[未知] {line}")
                
                print("\n" + "-"*60)
                print("✅ 流式响应测试成功")
                print("-"*60)
                
            except Exception as e:
                print(f"\n❌ 流式响应解析失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(f"  响应: {response.text}")


def test_stream_chat_with_conversation():
    """测试流式聊天（带对话 ID）"""
    print("\n" + "="*60)
    print("测试 2: 流式聊天（带对话 ID）")
    print("="*60)

    # 创建对话
    print("\n创建对话...")
    response = requests.post(
        f"{API_BASE_URL}/conversations",
        json={"metadata": {"test": "stream"}},
        timeout=10,
    )

    if response.status_code != 200:
        print(f"❌ 创建对话失败: {response.status_code}")
        return

    conversation_id = response.json()["conversation_id"]
    print(f"✅ 对话创建成功: {conversation_id}")

    # 发送第一条消息
    print("\n第 1 轮（无历史）:")
    response = requests.post(
        f"{API_BASE_URL}/chat/stream",
        json={
            "question": "什么是车载测试？",
            "conversation_id": conversation_id,
            "use_history": False,
            "use_rerank": False,
            "top_k": 3,
        },
        timeout=60,
        stream=True,
    )

    print("流式响应:")
    for line in response.iter_lines():
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str:
                chunk = json.loads(data_str)
                if chunk.get("type") == "content":
                    print(chunk.get("content", ""), end="", flush=True)

    # 发送第二条消息（带历史）
    print("\n\n第 2 轮（使用历史）:")
    response = requests.post(
        f"{API_BASE_URL}/chat/stream",
        json={
            "question": "测试流程有哪些步骤？",
            "conversation_id": conversation_id,
            "use_history": True,
            "use_rerank": False,
            "top_k": 3,
        },
        timeout=60,
        stream=True,
    )

    print("流式响应:")
    for line in response.iter_lines():
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str:
                chunk = json.loads(data_str)
                if chunk.get("type") == "content":
                    print(chunk.get("content", ""), end="", flush=True)

    # 删除对话
    print("\n\n删除对话...")
    requests.delete(
        f"{API_BASE_URL}/conversations/{conversation_id}",
        timeout=10,
    )
    print("✅ 对话已删除")


def test_stream_with_rerank():
    """测试流式聊天（带重排序）"""
    print("\n" + "="*60)
    print("测试 3: 流式聊天（带重排序）")
    print("="*60)

    response = requests.post(
        f"{API_BASE_URL}/chat/stream",
        json={
            "question": "如何诊断车载电源系统的故障？",
            "conversation_id": None,
            "use_history": False,
            "use_rerank": True,  # 启用重排序
            "top_k": 5,
        },
        timeout=60,
        stream=True,
    )

    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        return

    print("流式响应（启用重排序）:")
    rerank_info = None
    
    for line in response.iter_lines():
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str:
                chunk = json.loads(data_str)
                
                chunk_type = chunk.get("type", "unknown")
                
                if chunk_type == "question":
                    print(f"\n[问题] {chunk.get('content', '')}")
                elif chunk_type == "content":
                    print(chunk.get("content", ""), end="", flush=True)
                elif chunk_type == "done":
                    print(f"\n[完成]")
                    if chunk.get("metadata"):
                        rerank_info = chunk["metadata"]
                        print(f"  - 重排序: {rerank_info.get('reranked', False)}")
                        if rerank_info.get('reranked'):
                            print(f"  - 重排序方法: {rerank_info.get('rerank_method', '')}")
                        print(f"  - 源文档数量: {chunk.get('source_count', 0)}")


def test_stream_performance():
    """测试流式性能"""
    print("\n" + "="*60)
    print("测试 4: 流式性能")
    print("="*60)

    question = "车载测试中常用的测试标准有哪些？"

    # 测试流式响应时间
    start_time = time.time()
    
    response = requests.post(
        f"{API_BASE_URL}/chat/stream",
        json={
            "question": question,
            "use_history": False,
            "top_k": 3,
        },
        timeout=60,
        stream=True,
    )

    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        return

    first_chunk_time = None
    last_chunk_time = None
    chunk_count = 0

    for line in response.iter_lines():
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str:
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                
                chunk = json.loads(data_str)
                if chunk.get("type") != "error":
                    last_chunk_time = time.time()
                    chunk_count += 1

    total_time = time.time() - start_time
    first_response_time = (first_chunk_time - start_time) * 1000  # ms
    generation_time = (last_chunk_time - first_chunk_time) * 1000  # ms

    print(f"\n性能指标:")
    print(f"  - 总响应时间: {total_time:.2f} 秒")
    print(f"  - 首个 chunk 响应时间: {first_response_time:.0f} ms")
    print(f"  - 生成时间: {generation_time:.0f} ms")
    print(f"  - chunk 数量: {chunk_count}")
    print(f"  - 平均 chunk 间隔: {(generation_time / chunk_count) if chunk_count > 0 else 0:.0f} ms")


def main():
    """主测试函数"""
    print("\n" + "#"*60)
    print("#  mPower_Rag 流式输出测试")
    print("#"*60)

    try:
        # 测试 1: 基本流式聊天
        test_stream_chat()

        # 测试 2: 流式聊天（带对话 ID）
        # test_stream_chat_with_conversation()  # 可选，如果对话 API 可用

        # 测试 3: 流式聊天（带重排序）
        test_stream_with_rerank()

        # 测试 4: 流式性能
        test_stream_performance()

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
