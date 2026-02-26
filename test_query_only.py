"""
API查询测试脚本（只测试查询功能）
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_query():
    """只测试查询功能"""
    
    # 1. 测试根路径
    print("1. 测试根路径...")
    response = requests.get(f"{BASE_URL}/")
    print(f"响应: {response.json()}")
    
    # 2. 测试示例问题
    print("\n2. 测试示例问题...")
    response = requests.get(f"{BASE_URL}/api/v1/examples")
    print(f"示例问题: {response.json()}")
    
    # 3. 查询蓝牙相关
    print("\n3. 查询蓝牙相关...")
    query_data = {
        "query": "车载蓝牙模块的连接稳定性测试方法",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"蓝牙查询结果: {response.json()}")
    
    # 4. 查询ECU相关
    print("\n4. 查询ECU相关...")
    query_data = {
        "query": "ECU故障诊断流程是什么？",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"ECU查询结果: {response.json()}")
    
    # 5. 查询其他主题
    print("\n5. 查询CAN总线...")
    query_data = {
        "query": "CAN总线通信测试标准",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"CAN查询结果: {response.json()}")
    
    # 6. 查询其他相关主题
    print("\n6. 查询发动机性能...")
    query_data = {
        "query": "发动机性能测试",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"发动机查询结果: {response.json()}")

if __name__ == "__main__":
    print("开始测试mPower_Rag API查询功能...")
    try:
        test_query()
        print("\n[SUCCESS] 查询测试完成！")
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()