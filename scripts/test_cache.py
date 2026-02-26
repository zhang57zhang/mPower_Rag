"""
缓存功能测试脚本
测试 Redis 缓存的所有功能
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


def test_cache_stats():
    """测试 1: 获取缓存统计"""
    print("\n" + "="*60)
    print("测试 1: 获取缓存统计")
    print("="*60)

    response = requests.get(
        f"{API_BASE_URL}/cache/stats",
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "缓存统计信息")

        # 检查缓存状态
        if result.get("enabled"):
            print("✅ 缓存已启用")
            print(f"  - 总键数: {result.get('total_keys', 0)}")
            print(f"  - 前缀统计:")
            for prefix, count in result.get("prefix_counts", {}).items():
                print(f"    - {prefix}: {count} 个键")
        else:
            print("❌ 缓存未启用")
    else:
        print(f"❌ 获取缓存统计失败: {response.status_code}")


def test_query_cache():
    """测试 2: 查询缓存"""
    print("\n" + "="*60)
    print("测试 2: 查询缓存")
    print("="*60)

    questions = [
        "什么是车载测试？",
        "车载 CAN 总线测试的标准流程是什么？",
    ]

    for i, question in enumerate(questions):
        print(f"\n问题 {i+1}: {question}")
        print("-"*60)

        # 第一次查询（应该不命中缓存）
        print("第 1 次查询（应该不命中）:")
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "question": question,
                "skip_cache": True,  # 跳过缓存
            },
            timeout=30,
        )
        first_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            cached = result.get("cached", False)
            print(f"  - 响应时间: {first_time:.2f} 秒")
            print(f"  - 来自缓存: {cached}")
            print(f"  - 答案长度: {len(result.get('answer', ''))} 字符")
        else:
            print(f"  ❌ 查询失败: {response.status_code}")
            continue

        # 第二次查询（应该命中缓存）
        print("第 2 次查询（应该命中）:")
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "question": question,
                "skip_cache": False,  # 使用缓存
            },
            timeout=30,
        )
        second_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            cached = result.get("cached", False)
            print(f"  - 响应时间: {second_time:.2f} 秒")
            print(f"  - 来自缓存: {cached}")

            if cached:
                speedup = first_time / second_time if second_time > 0 else 1
                print(f"  - 性能提升: {speedup:.1f}x")
            else:
                print(f"  ⚠️ 缓存未命中")

            if not cached:
                print(f"  ⚠️ 答案不一致（缓存问题？）")
        else:
            print(f"  ❌ 查询失败: {response.status_code}")


def test_stream_with_cache():
    """测试 3: 流式查询（带缓存）"""
    print("\n" + "="*60)
    print("测试 3: 流式查询（带缓存）")
    print("="*60)

    question = "如何诊断车载电源系统的故障？"

    # 第一次查询（不使用缓存）
    print("第 1 次流式查询（不使用缓存）:")
    start_time = time.time()
    response = requests.post(
        f"{API_BASE_URL}/chat/stream",
        json={
            "question": question,
            "skip_cache": True,
        },
        timeout=60,
        stream=True,
    )

    first_time = time.time() - start_time
    chunks = 0

    for line in response.iter_lines():
        if line.startswith("data: "):
            chunks += 1

    print(f"  - 总时间: {first_time:.2f} 秒")
    print(f"  - 收到的块数: {chunks}")

    # 第二次查询（使用缓存）
    print("\n第 2 次流式查询（使用缓存）:")
    start_time = time.time()
    response = requests.post(
        f"{API_BASE_URL}/chat/stream",
        json={
            "question": question,
            "skip_cache": False,
        },
        timeout=60,
        stream=True,
    )

    second_time = time.time() - start_time
    cached_chunks = 0

    for line in response.iter_lines():
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str:
                chunk = json.loads(data_str)
                if chunk.get("type") == "content":
                    cached_chunks += 1
                elif chunk.get("type") == "done":
                    cached = chunk.get("metadata", {}).get("cached", False)
                    if cached:
                        print(f"  ✅ 缓存命中")
                    print(f"  - 总时间: {second_time:.2f} 秒")
                    print(f"  - 收到的块数: {cached_chunks}")

                    if first_time > 0:
                        speedup = first_time / second_time if second_time > 0 else 1
                        print(f"  - 性能提升: {speedup:.1f}x")
                    else:
                        print(f"  ⚠️ 性能下降（可能是流式开销）")
                    break


def test_clear_cache_by_prefix():
    """测试 4: 清空指定前缀的缓存"""
    print("\n" + "="*60)
    print("测试 4: 清空指定前缀的缓存")
    print("="*60)

    prefixes = ["query", "retrieval", "llm", "rerank"]

    for prefix in prefixes:
        print(f"\n清空前缀: {prefix}")

        response = requests.post(
            f"{API_BASE_URL}/cache/clear",
            json={"prefix": prefix},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ {result.get('message', '操作完成')}")
            print(f"  - 清空数量: {result.get('cleared_count', 0)} 个键")
        else:
            print(f"  ❌ 清空失败: {response.status_code}")


def test_clear_all_cache():
    """测试 5: 清空所有缓存"""
    print("\n" + "="*60)
    print("测试 5: 清空所有缓存")
    print("="*60)

    response = requests.post(
        f"{API_BASE_URL}/cache/clear_all",
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print_json(result, "清空所有缓存")
        print(f"  - {result.get('message', '操作完成')}")
    else:
        print(f"❌ 清空失败: {response.status_code}")


def test_cache_concurrent_requests():
    """测试 6: 并发请求缓存"""
    print("\n" + "="*60)
    print("测试 6: 并发请求缓存")
    print("="*60)

    import concurrent.futures

    question = "什么是车载测试？"

    def query_with_index(index):
        """带索引的查询"""
        start_time = time.time()

        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "question": question,
            "skip_cache": False,
            "use_history": False,
            "use_rerank": False,
            "top_k": 3,
            },
            timeout=30,
        )

        elapsed = time.time() - start_time
        cached = response.json().get("cached", False) if response.status_code == 200 else False

        return {
            "index": index,
            "time": elapsed,
            "cached": cached,
            "success": response.status_code == 200,
        }

    # 执行 10 次并发查询
    num_requests = 10

    print(f"\n执行 {num_requests} 次并发查询...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(query_with_index, i) for i in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # 分析结果
    successful = [r for r in results if r["success"]]
    cached = [r for r in successful if r["cached"]]

    total_time = sum(r["time"] for r in successful)
    avg_time = total_time / len(successful) if successful else 0

    print(f"\n并发请求结果:")
    print(f"  - 成功请求数: {len(successful)}/{num_requests}")
    print(f"  - 缓存命中数: {len(cached)}/{len(successful)}")
    print(f"  - 缓存命中率: {(len(cached) / len(successful) * 100) if successful else 0:.1f}%")
    print(f"  - 平均响应时间: {avg_time:.2f} 秒")
    print(f"  - 总时间: {total_time:.2f} 秒")


def main():
    """主测试函数"""
    print("\n" + "#"*60)
    print("#  mPower_Rag 缓存功能测试")
    print("#"*60)

    try:
        # 测试 1: 获取缓存统计
        test_cache_stats()

        # 测试 2: 查询缓存
        test_query_cache()

        # 测试 3: 流式查询（带缓存）
        test_stream_with_cache()

        # 测试 4: 清空指定前缀
        test_clear_cache_by_prefix()

        # 测试 5: 清空所有缓存
        test_clear_all_cache()

        # 测试 6: 并发请求
        test_cache_concurrent_requests()

    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)

    # 最后统计
    print("\n" + "#"*60)
    print("#  测试总结")
    print("#"*60)

    print("\n建议：")
    print("1. 监控 Redis 内存使用")
    print("2. 设置合理的缓存 TTL")
    print("3. 根据访问模式优化缓存策略")
    print("4. 在生产环境启用持久化（RDB/AOF）")
    print("5. 监控缓存命中率")

    print("\n下一步：")
    print("- 调整缓存参数（TTL、键前缀等）")
    print("- 根据实际负载优化配置")
    print("- 添加缓存预热功能")
    print("- 实现缓存淘汰策略（LRU、LFU等）")


if __name__ == "__main__":
    main()
