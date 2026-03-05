"""
Phase 2 功能测试脚本
测试批量上传、目录导入等新功能
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"


def test_batch_upload():
    """测试批量上传"""
    print("\n=== 测试批量上传 ===")

    # 准备测试文件
    files = [
        ('files', ('test_batch.txt', open('test_batch.txt', 'rb'), 'text/plain')),
        ('files', ('test_batch2.txt', open('test_batch2.txt', 'rb'), 'text/plain'))
    ]

    try:
        response = requests.post(f"{BASE_URL}/documents/batch-upload", files=files)
        result = response.json()

        print(f"状态码: {response.status_code}")
        print(f"消息: {result.get('message', 'N/A')}")
        print(f"成功: {result.get('success_count', 0)}, 失败: {result.get('failed_count', 0)}")
        print(f"总文档数: {result.get('total_documents', 0)}")

        # 显示详细结果
        for res in result.get('results', []):
            status = "[OK]" if res['success'] else "[FAIL]"
            print(f"  {status} {res['filename']}: {res.get('format', 'N/A')}")

        return response.status_code == 200

    finally:
        # 关闭文件
        for _, file_tuple in files:
            file_tuple[1].close()


def test_import_directory():
    """测试导入目录"""
    print("\n=== 测试导入目录 ===")

    data = {
        "directory_path": "knowledge_base",
        "recursive": False,
        "file_extensions": [".txt"]
    }

    response = requests.post(f"{BASE_URL}/documents/import-directory", json=data)
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"消息: {result.get('message', 'N/A')}")
    print(f"目录: {result.get('directory', 'N/A')}")
    print(f"找到文件: {result.get('files_found', 0)}")
    print(f"导入成功: {result.get('imported_count', 0)}")
    print(f"总文档数: {result.get('total_documents', 0)}")

    # 显示详细结果
    for res in result.get('results', [])[:3]:  # 只显示前3个
        status = "[OK]" if res['success'] else "[FAIL]"
        print(f"  {status} {res['filename']}: {res.get('format', 'N/A')}")

    return response.status_code == 200


def test_list_after_phase2():
    """测试Phase 2后的文档列表"""
    print("\n=== 测试文档列表（Phase 2后）===")

    response = requests.get(f"{BASE_URL}/documents/list")
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"文档总数: {result['total']}")

    # 按格式统计
    format_count = {}
    for doc in result['documents']:
        fmt = doc['metadata'].get('format', 'unknown')
        format_count[fmt] = format_count.get(fmt, 0) + 1

    print("格式分布:")
    for fmt, count in format_count.items():
        print(f"  {fmt}: {count}个")

    return response.status_code == 200


def test_stats_after_phase2():
    """测试统计信息（Phase 2后）"""
    print("\n=== 测试统计信息（Phase 2后）===")

    response = requests.get(f"{BASE_URL}/documents/stats")
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"文档总数: {result.get('total_documents', 0)}")
    print(f"引擎状态: {result.get('engine_status', {}).get('status', 'N/A')}")

    return response.status_code == 200


def test_query_after_phase2():
    """测试查询功能（Phase 2后）"""
    print("\n=== 测试查询功能（Phase 2后）===")

    data = {
        "query": "测试",
        "top_k": 3
    }

    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()

    print(f"状态码: {response.status_code}")

    if response.status_code == 200 and 'answer' in result:
        print(f"回答: {result['answer'][:100]}...")
        print(f"来源数量: {len(result.get('sources', []))}")
        return True
    else:
        print(f"查询失败: {result.get('detail', 'Unknown error')}")
        return False


def main():
    """运行所有Phase 2测试"""
    print("=" * 60)
    print("mPower_Rag Phase 2 功能测试")
    print("=" * 60)

    results = {}

    # 1. 测试批量上传
    try:
        results['batch_upload'] = test_batch_upload()
    except Exception as e:
        results['batch_upload'] = False
        print(f"批量上传测试异常: {e}")

    # 2. 测试导入目录
    try:
        results['import_directory'] = test_import_directory()
    except Exception as e:
        results['import_directory'] = False
        print(f"导入目录测试异常: {e}")

    # 3. 测试文档列表
    results['list_after_phase2'] = test_list_after_phase2()

    # 4. 测试统计信息
    results['stats_after_phase2'] = test_stats_after_phase2()

    # 5. 测试查询功能
    try:
        results['query_after_phase2'] = test_query_after_phase2()
    except Exception as e:
        results['query_after_phase2'] = False
        print(f"查询测试异常: {e}")

    # 打印总结
    print("\n" + "=" * 60)
    print("Phase 2 测试总结")
    print("=" * 60)

    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

    return all(results.values())


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
