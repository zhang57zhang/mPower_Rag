"""
API测试脚本（简化版）
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_api():
    """测试API基本功能"""
    
    # 1. 测试根路径
    print("1. 测试根路径...")
    response = requests.get(f"{BASE_URL}/")
    print(f"响应: {response.json()}")
    
    # 2. 测试示例问题
    print("\n2. 测试示例问题...")
    response = requests.get(f"{BASE_URL}/api/v1/examples")
    print(f"示例问题: {response.json()}")
    
    # 3. 上传蓝牙测试文档
    print("\n3. 上传蓝牙测试文档...")
    upload_files = [
        ('file', ('bluetooth_test_guide.txt', open('knowledge_base/bluetooth_test_guide.txt', 'r', encoding='utf-8'), 'text/plain'))
    ]
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=upload_files)
    print(f"上传结果: {response.json()}")
    
    # 4. 上传ECU诊断文档
    print("\n4. 上传ECU诊断文档...")
    upload_files = [
        ('file', ('ecu_diagnosis_guide.txt', open('knowledge_base/ecu_diagnosis_guide.txt', 'r', encoding='utf-8'), 'text/plain'))
    ]
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=upload_files)
    print(f"上传结果: {response.json()}")
    
    # 5. 查询蓝牙相关
    print("\n5. 查询蓝牙相关...")
    query_data = {
        "query": "车载蓝牙模块的连接稳定性测试方法",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"蓝牙查询结果: {response.json()}")
    
    # 6. 查询ECU相关
    print("\n6. 查询ECU相关...")
    query_data = {
        "query": "ECU故障诊断流程是什么？",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"ECU查询结果: {response.json()}")
    
    # 7. 查询其他主题
    print("\n7. 查询CAN总线...")
    query_data = {
        "query": "CAN总线通信测试标准",
        "use_rerank": False,
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=query_data)
    print(f"CAN查询结果: {response.json()}")

if __name__ == "__main__":
    print("开始测试mPower_Rag API...")
    try:
        test_api()
        print("\n[SUCCESS] 所有测试完成！")
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()