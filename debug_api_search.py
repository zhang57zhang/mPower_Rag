"""
调试API中的搜索功能
"""
import requests

BASE_URL = "http://localhost:8000"

def debug_search_in_api():
    """在API中调试搜索功能"""
    
    print("在API中调试搜索功能...")
    
    # 先获取文档统计
    print("\n1. 获取文档统计...")
    response = requests.get(f"{BASE_URL}/api/v1/documents/stats")
    stats = response.json()
    print(f"文档统计: {stats}")
    
    # 添加一个测试查询，看看搜索过程
    print("\n2. 测试查询并查看搜索过程...")
    query_data = {
        "query": "蓝牙测试",
        "use_rerank": False,
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    result = response.json()
    
    print(f"查询结果: {result}")
    
    # 测试不同的查询
    test_queries = ["蓝牙", "测试", "ECU", "诊断"]
    
    for query in test_queries:
        print(f"\n3. 测试短查询: '{query}'")
        query_data = {
            "query": query,
            "use_rerank": False,
            "top_k": 3
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
        result = response.json()
        print(f"结果: {result}")
        
        if result['sources']:
            print(f"  找到来源: {len(result['sources'])}个")
        else:
            print("  未找到来源")

if __name__ == "__main__":
    debug_search_in_api()