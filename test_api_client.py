"""
API功能测试脚本（修复版）
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_query():
    """测试查询功能"""
    print("\n=== 测试查询功能 ===")

    data = {
        "query": "车载蓝牙测试",
        "top_k": 3
    }

    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")

    if response.status_code == 200 and 'answer' in result:
        print(f"回答: {result['answer'][:100]}...")
        print(f"来源数量: {len(result.get('sources', []))}")
        return True
    else:
        print(f"查询失败: {result.get('detail', 'Unknown error')}")
        return False


def test_upload():
    """测试文档上传"""
    print("\n=== 测试文档上传 ===")

    file_path = "test_document.txt"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/documents/upload", files=files)

    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"消息: {result.get('message', 'N/A')}")
    print(f"文件名: {result.get('filename', 'N/A')}")
    print(f"格式: {result.get('format', 'N/A')}")
    print(f"当前文档数: {result.get('document_count', 'N/A')}")

    return response.status_code == 200


def test_list_documents():
    """测试列出文档"""
    print("\n=== 测试列出文档 ===")

    response = requests.get(f"{BASE_URL}/documents/list")
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"文档总数: {result['total']}")

    for doc in result['documents']:
        print(f"  - ID: {doc['id']}")
        print(f"    文件名: {doc['metadata']['filename']}")
        print(f"    格式: {doc['metadata']['format']}")

    return response.status_code == 200, result['documents']


def test_delete_document(doc_id):
    """测试删除文档"""
    print(f"\n=== 测试删除文档: {doc_id} ===")

    response = requests.delete(f"{BASE_URL}/documents/{doc_id}")
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"消息: {result.get('message', 'N/A')}")
    print(f"剩余文档数: {result.get('remaining_documents', 'N/A')}")

    return response.status_code == 200


def test_batch_delete(doc_ids):
    """测试批量删除"""
    print(f"\n=== 测试批量删除: {len(doc_ids)}个文档 ===")

    data = {"doc_ids": doc_ids}
    response = requests.post(f"{BASE_URL}/documents/batch-delete", json=data)
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"消息: {result.get('message', 'N/A')}")
    print(f"成功: {result.get('success_count', 0)}, 失败: {result.get('failed_count', 0)}")

    return response.status_code == 200


def test_external_api_import():
    """测试从外部API导入"""
    print("\n=== 测试外部API导入 ===")

    data = {
        "url": "https://httpbin.org/json",
        "metadata": {
            "test": "external_api_import"
        }
    }

    response = requests.post(f"{BASE_URL}/documents/import-from-api", json=data)
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"消息: {result.get('message', 'N/A')}")
    print(f"源URL: {result.get('source_url', 'N/A')}")

    return response.status_code == 200


def test_external_query():
    """测试外部系统查询"""
    print("\n=== 测试外部系统查询 ===")

    data = {
        "query": "ECU诊断",
        "top_k": 2
    }

    response = requests.post(f"{BASE_URL}/query-from-external", json=data)
    result = response.json()

    print(f"状态码: {response.status_code}")

    if response.status_code == 200 and 'answer' in result:
        print(f"回答: {result['answer'][:100]}...")
        print(f"API版本: {result.get('api_version', 'N/A')}")
        return True
    else:
        print(f"查询失败: {result.get('detail', 'Unknown error')}")
        return False


def test_stats():
    """测试统计信息"""
    print("\n=== 测试统计信息 ===")

    response = requests.get(f"{BASE_URL}/documents/stats")
    result = response.json()

    print(f"状态码: {response.status_code}")
    print(f"文档总数: {result.get('total_documents', 0)}")
    print(f"引擎状态: {result.get('engine_status', {}).get('status', 'N/A')}")

    return response.status_code == 200


def main():
    """运行所有测试"""
    print("=" * 60)
    print("mPower_Rag API 功能测试")
    print("=" * 60)

    results = {}

    # 1. 测试统计信息
    results['stats'] = test_stats()

    # 2. 测试列出文档
    success, docs = test_list_documents()
    results['list'] = success

    # 3. 测试上传
    results['upload'] = test_upload()

    # 4. 再次列出文档（验证上传）
    success, docs = test_list_documents()
    results['list_after_upload'] = success

    # 5. 测试查询
    try:
        results['query'] = test_query()
    except Exception as e:
        results['query'] = False
        print(f"查询测试异常: {e}")

    # 6. 测试外部查询
    try:
        results['external_query'] = test_external_query()
    except Exception as e:
        results['external_query'] = False
        print(f"外部查询测试异常: {e}")

    # 7. 测试删除（删除刚上传的文档）
    if docs:
        test_doc = docs[-1]  # 删除最后一个（刚上传的）
        results['delete'] = test_delete_document(test_doc['id'])
    else:
        results['delete'] = False
        print("\n跳过删除测试：没有文档")

    # 8. 测试外部API导入
    try:
        results['external_import'] = test_external_api_import()
    except Exception as e:
        results['external_import'] = False
        print(f"外部API导入失败: {e}")

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
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
