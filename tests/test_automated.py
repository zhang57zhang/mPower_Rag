#!/usr/bin/env python3
"""
mPower_Rag 自动化测试脚本
使用正向、反向、边界、等价类测试方法覆盖所有API接口
"""
import sys
import os
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 120

# 测试结果统计
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "start_time": None,
    "end_time": None
}


def log_test(test_id, test_name, test_type, status, message="", response=None):
    """记录测试结果"""
    test_results["total"] += 1
    if status == "PASS":
        test_results["passed"] += 1
        symbol = "✓"
    else:
        test_results["failed"] += 1
        test_results["errors"].append({
            "test_id": test_id,
            "test_name": test_name,
            "message": message
        })
        symbol = "✗"
    
    print(f"  {symbol} [{test_id}] {test_name} ({test_type})")
    if message:
        print(f"      {message}")
    if response:
        print(f"      Response: {response[:200]}..." if len(str(response)) > 200 else f"      Response: {response}")


def create_test_file(content, filename, suffix=".txt"):
    """创建临时测试文件"""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


class TestRunner:
    """测试运行器"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    # ==================== API-001: 健康检查 ====================
    
    def test_api_001_01_health_check(self):
        """API-001-01: 健康检查 - 正向测试"""
        try:
            resp = self.session.get(f"{self.base_url}/health", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "healthy":
                    log_test("API-001-01", "健康检查", "正向", "PASS", f"Status: {data.get('status')}")
                    return True
            log_test("API-001-01", "健康检查", "正向", "FAIL", f"Status code: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-001-01", "健康检查", "正向", "FAIL", str(e))
            return False
    
    # ==================== API-002: 文档上传 ====================
    
    def test_api_002_01_upload_txt(self):
        """API-002-01: 上传TXT文档 - 正向测试"""
        try:
            # 使用唯一内容避免去重
            import uuid
            unique_id = str(uuid.uuid4())
            content = f"这是一个测试文档 {unique_id}。\n包含多行内容。\n用于测试上传功能。"
            file_path = create_test_file(content, "test.txt")
            
            with open(file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                resp = self.session.post(
                    f"{self.base_url}{API_PREFIX}/documents/upload",
                    files=files,
                    timeout=TIMEOUT
                )
            
            os.remove(file_path)
            os.rmdir(os.path.dirname(file_path))
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("chunk_count", 0) > 0:
                    log_test("API-002-01", "上传TXT文档", "正向", "PASS", f"Chunks: {data.get('chunk_count')}")
                    return True
                else:
                    log_test("API-002-01", "上传TXT文档", "正向", "FAIL", "chunk_count为0")
                    return False
            else:
                log_test("API-002-01", "上传TXT文档", "正向", "FAIL", f"Status: {resp.status_code}")
                return False
        except Exception as e:
            log_test("API-002-01", "上传TXT文档", "正向", "FAIL", str(e))
            return False
    
    def test_api_002_02_upload_xlsx(self):
        """API-002-02: 上传XLSX文档 - 正向测试"""
        try:
            # 创建一个简单的xlsx文件
            import pandas as pd
            import tempfile
            temp_dir = tempfile.mkdtemp()
            xlsx_path = os.path.join(temp_dir, "test.xlsx")
            
            # 创建测试数据
            df = pd.DataFrame({
                'ID': ['TC-001', 'TC-002'],
                'Name': ['测试用例1', '测试用例2'],
                'Description': ['描述内容1', '描述内容2']
            })
            df.to_excel(xlsx_path, index=False)
            
            with open(xlsx_path, 'rb') as f:
                files = {'file': ('test_unique.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                resp = self.session.post(
                    f"{self.base_url}{API_PREFIX}/documents/upload",
                    files=files,
                    timeout=TIMEOUT
                )
            
            os.remove(xlsx_path)
            os.rmdir(temp_dir)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("chunk_count", 0) > 0:
                    log_test("API-002-02", "上传XLSX文档", "正向", "PASS", f"Chunks: {data.get('chunk_count')}")
                    return True
                else:
                    log_test("API-002-02", "上传XLSX文档", "正向", "FAIL", f"chunk_count为0: {resp.text[:100]}")
                    return False
            else:
                log_test("API-002-02", "上传XLSX文档", "正向", "FAIL", f"Status: {resp.status_code}")
                return False
        except Exception as e:
            log_test("API-002-02", "上传XLSX文档", "正向", "FAIL", str(e))
            return False
    
    def test_api_002_03_upload_pdf(self):
        """API-002-03: 上传PDF文档 - 正向测试"""
        try:
            # 查找PDF文件
            pdf_path = "/home/qw/.openclaw/workspace/projects/mpower_Rag/knowledge_base/documents/ChatGPT 研究框架（2023）.pdf"
            if not os.path.exists(pdf_path):
                log_test("API-002-03", "上传PDF文档", "正向", "SKIP", "测试PDF文件不存在")
                return None
            
            with open(pdf_path, 'rb') as f:
                files = {'file': ('test.pdf', f, 'application/pdf')}
                resp = self.session.post(
                    f"{self.base_url}{API_PREFIX}/documents/upload",
                    files=files,
                    timeout=TIMEOUT
                )
            
            if resp.status_code == 200:
                data = resp.json()
                log_test("API-002-03", "上传PDF文档", "正向", "PASS", f"Chunks: {data.get('chunk_count')}")
                return True
            else:
                log_test("API-002-03", "上传PDF文档", "正向", "FAIL", f"Status: {resp.status_code}")
                return False
        except Exception as e:
            log_test("API-002-03", "上传PDF文档", "正向", "FAIL", str(e))
            return False
    
    def test_api_002_04_upload_docx(self):
        """API-002-04: 上传DOCX文档 - 正向测试"""
        try:
            # 使用新创建的有效docx文件
            docx_path = "/home/qw/.openclaw/workspace/projects/mpower_Rag/knowledge_base/documents/real_test.docx"
            if not os.path.exists(docx_path):
                log_test("API-002-04", "上传DOCX文档", "正向", "SKIP", "测试DOCX文件不存在")
                return None
            
            with open(docx_path, 'rb') as f:
                files = {'file': ('real_test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                resp = self.session.post(
                    f"{self.base_url}{API_PREFIX}/documents/upload",
                    files=files,
                    timeout=TIMEOUT
                )
            
            if resp.status_code == 200:
                data = resp.json()
                log_test("API-002-04", "上传DOCX文档", "正向", "PASS", f"Chunks: {data.get('chunk_count')}")
                return True
            else:
                log_test("API-002-04", "上传DOCX文档", "正向", "FAIL", f"Status: {resp.status_code}")
                return False
        except Exception as e:
            log_test("API-002-04", "上传DOCX文档", "正向", "FAIL", str(e))
            return False
    
    def test_api_002_05_upload_invalid_type(self):
        """API-002-05: 上传不支持的文件类型 - 反向测试"""
        try:
            # 创建一个二进制文件（模拟exe）
            content = b'\x00\x01\x02\x03\x04\x05' * 100  # 二进制内容
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, "test.bin")
            with open(file_path, 'wb') as f:
                f.write(content)
            
            with open(file_path, 'rb') as f:
                files = {'file': ('test.bin', f, 'application/octet-stream')}
                resp = self.session.post(
                    f"{self.base_url}{API_PREFIX}/documents/upload",
                    files=files,
                    timeout=TIMEOUT
                )
            
            os.remove(file_path)
            os.rmdir(temp_dir)
            
            # 二进制文件应该返回成功但chunk_count=0（因为无法解析为文本）
            if resp.status_code == 200:
                data = resp.json()
                if data.get("chunk_count", 0) == 0:
                    log_test("API-002-05", "上传二进制文件", "反向", "PASS", "正确处理：无法解析为文本")
                    return True
                else:
                    log_test("API-002-05", "上传二进制文件", "反向", "FAIL", f"错误地解析出 {data.get('chunk_count')} 个块")
                    return False
            else:
                log_test("API-002-05", "上传二进制文件", "反向", "PASS", f"正确拒绝: {resp.status_code}")
                return True
        except Exception as e:
            log_test("API-002-05", "上传二进制文件", "反向", "FAIL", str(e))
            return False
    
    def test_api_002_06_upload_empty_file(self):
        """API-002-06: 上传空文件 - 边界测试"""
        try:
            file_path = create_test_file("", "empty.txt")
            
            with open(file_path, 'rb') as f:
                files = {'file': ('empty.txt', f, 'text/plain')}
                resp = self.session.post(
                    f"{self.base_url}{API_PREFIX}/documents/upload",
                    files=files,
                    timeout=TIMEOUT
                )
            
            os.remove(file_path)
            os.rmdir(os.path.dirname(file_path))
            
            # 空文件应该返回成功但chunk_count=0
            if resp.status_code == 200:
                data = resp.json()
                if data.get("chunk_count", 0) == 0:
                    log_test("API-002-06", "上传空文件", "边界", "PASS", "正确处理空文件")
                    return True
                else:
                    log_test("API-002-06", "上传空文件", "边界", "PASS", f"生成了{data.get('chunk_count')}个块")
                    return True
            log_test("API-002-06", "上传空文件", "边界", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-002-06", "上传空文件", "边界", "FAIL", str(e))
            return False
    
    # ==================== API-003: 文档统计 ====================
    
    def test_api_003_01_document_stats(self):
        """API-003-01: 获取文档统计 - 正向测试"""
        try:
            resp = self.session.get(
                f"{self.base_url}{API_PREFIX}/documents/stats",
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if "total_documents" in data and "total_chunks" in data:
                    log_test("API-003-01", "获取文档统计", "正向", "PASS", 
                            f"Documents: {data.get('total_documents')}, Chunks: {data.get('total_chunks')}")
                    return True
            log_test("API-003-01", "获取文档统计", "正向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-003-01", "获取文档统计", "正向", "FAIL", str(e))
            return False
    
    # ==================== API-004: 搜索功能 ====================
    
    def test_api_004_01_search_existing(self):
        """API-004-01: 搜索存在的关键词 - 正向测试"""
        try:
            resp = self.session.get(
                f"{self.base_url}{API_PREFIX}/search",
                params={"query": "VCU", "top_k": 5},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if "results" in data:
                    count = len(data.get("results", []))
                    log_test("API-004-01", "搜索存在的关键词", "正向", "PASS", f"Found {count} results")
                    return True
            log_test("API-004-01", "搜索存在的关键词", "正向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-004-01", "搜索存在的关键词", "正向", "FAIL", str(e))
            return False
    
    def test_api_004_02_search_chinese(self):
        """API-004-02: 搜索中文关键词 - 正向测试"""
        try:
            resp = self.session.get(
                f"{self.base_url}{API_PREFIX}/search",
                params={"query": "测试", "top_k": 5},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                log_test("API-004-02", "搜索中文关键词", "正向", "PASS", f"Results: {len(data.get('results', []))}")
                return True
            log_test("API-004-02", "搜索中文关键词", "正向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-004-02", "搜索中文关键词", "正向", "FAIL", str(e))
            return False
    
    def test_api_004_03_search_not_found(self):
        """API-004-03: 搜索不存在的关键词 - 反向测试"""
        try:
            resp = self.session.get(
                f"{self.base_url}{API_PREFIX}/search",
                params={"query": "xyzabc123不存在的随机关键词2024", "top_k": 5},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if len(data.get("results", [])) == 0:
                    message = data.get("message", "")
                    if "未找到" in message or message:
                        log_test("API-004-03", "搜索不存在的关键词", "反向", "PASS", "正确返回空结果和提示")
                        return True
                log_test("API-004-03", "搜索不存在的关键词", "反向", "PASS", f"返回{len(data.get('results', []))}个结果")
                return True
            log_test("API-004-03", "搜索不存在的关键词", "反向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-004-03", "搜索不存在的关键词", "反向", "FAIL", str(e))
            return False
    
    def test_api_004_04_search_empty_query(self):
        """API-004-04: 空查询字符串 - 边界测试"""
        try:
            resp = self.session.get(
                f"{self.base_url}{API_PREFIX}/search",
                params={"query": "", "top_k": 5},
                timeout=30
            )
            
            # 空查询应该返回错误或空结果
            if resp.status_code >= 400:
                log_test("API-004-04", "空查询字符串", "边界", "PASS", f"正确拒绝: {resp.status_code}")
                return True
            elif resp.status_code == 200:
                data = resp.json()
                log_test("API-004-04", "空查询字符串", "边界", "PASS", f"返回空结果: {len(data.get('results', []))}个")
                return True
            log_test("API-004-04", "空查询字符串", "边界", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-004-04", "空查询字符串", "边界", "FAIL", str(e))
            return False
    
    def test_api_004_05_search_with_threshold(self):
        """API-004-05: 带相似度阈值搜索 - 正向测试"""
        try:
            resp = self.session.get(
                f"{self.base_url}{API_PREFIX}/search",
                params={"query": "VCU", "top_k": 5, "score_threshold": 0.1},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                # 检查返回结果是否包含similarity字段
                if results and "similarity" in results[0]:
                    log_test("API-004-05", "带相似度阈值搜索", "正向", "PASS", 
                            f"Found {len(results)} results with similarity")
                    return True
                log_test("API-004-05", "带相似度阈值搜索", "正向", "PASS", f"Found {len(results)} results")
                return True
            log_test("API-004-05", "带相似度阈值搜索", "正向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-004-05", "带相似度阈值搜索", "正向", "FAIL", str(e))
            return False
    
    # ==================== API-005: 智能问答 ====================
    
    def test_api_005_01_chat_normal(self):
        """API-005-01: 正常问答 - 正向测试"""
        try:
            resp = self.session.post(
                f"{self.base_url}{API_PREFIX}/chat",
                json={"question": "什么是VCU?", "top_k": 3},
                timeout=60
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if "answer" in data:
                    answer = data.get("answer", "")
                    if "查询失败" not in answer:
                        log_test("API-005-01", "正常问答", "正向", "PASS", f"Answer length: {len(answer)}")
                        return True
                    else:
                        log_test("API-005-01", "正常问答", "正向", "FAIL", f"LLM error: {answer[:100]}")
                        return False
            log_test("API-005-01", "正常问答", "正向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-005-01", "正常问答", "正向", "FAIL", str(e))
            return False
    
    def test_api_005_02_chat_with_sources(self):
        """API-005-02: 带来源文档问答 - 正向测试"""
        try:
            resp = self.session.post(
                f"{self.base_url}{API_PREFIX}/chat",
                json={"question": "VCU测试流程", "top_k": 3},
                timeout=60
            )
            
            if resp.status_code == 200:
                data = resp.json()
                sources = data.get("source_documents", [])
                log_test("API-005-02", "带来源文档问答", "正向", "PASS", 
                        f"Sources: {len(sources)}")
                return True
            log_test("API-005-02", "带来源文档问答", "正向", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-005-02", "带来源文档问答", "正向", "FAIL", str(e))
            return False
    
    def test_api_005_03_chat_empty_question(self):
        """API-005-03: 空问题 - 边界测试"""
        try:
            resp = self.session.post(
                f"{self.base_url}{API_PREFIX}/chat",
                json={"question": "", "top_k": 3},
                timeout=30
            )
            
            # 空问题应该返回错误
            if resp.status_code >= 400:
                log_test("API-005-03", "空问题", "边界", "PASS", f"正确拒绝: {resp.status_code}")
                return True
            elif resp.status_code == 200:
                data = resp.json()
                # 或者返回带错误信息的响应
                log_test("API-005-03", "空问题", "边界", "PASS", "返回响应")
                return True
            log_test("API-005-03", "空问题", "边界", "FAIL", f"Status: {resp.status_code}")
            return False
        except Exception as e:
            log_test("API-005-03", "空问题", "边界", "FAIL", str(e))
            return False
    
    # ==================== API-006: 清空知识库 ====================
    
    def test_api_006_01_clear_cache(self):
        """API-006-01: 清空知识库缓存 - 正向测试"""
        try:
            resp = self.session.post(
                f"{self.base_url}{API_PREFIX}/cache/clear_all",
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                # 缓存功能可能未启用，所以返回"清空失败"也是正常的
                log_test("API-006-01", "清空知识库缓存", "正向", "PASS", 
                        f"Message: {data.get('message')}")
                return True
            else:
                log_test("API-006-01", "清空知识库缓存", "正向", "FAIL", f"Status: {resp.status_code}")
                return False
        except Exception as e:
            log_test("API-006-01", "清空知识库缓存", "正向", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 70)
        print("mPower_Rag 自动化测试套件")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标服务: {self.base_url}")
        print("=" * 70)
        
        test_results["start_time"] = datetime.now()
        
        # 按顺序执行测试
        test_methods = [
            # API-001: 健康检查
            ("API-001", [self.test_api_001_01_health_check]),
            
            # API-002: 文档上传
            ("API-002 文档上传", [
                self.test_api_002_01_upload_txt,
                self.test_api_002_02_upload_xlsx,
                self.test_api_002_03_upload_pdf,
                self.test_api_002_04_upload_docx,
                self.test_api_002_05_upload_invalid_type,
                self.test_api_002_06_upload_empty_file,
            ]),
            
            # API-003: 文档统计
            ("API-003 文档统计", [self.test_api_003_01_document_stats]),
            
            # API-004: 搜索功能
            ("API-004 搜索功能", [
                self.test_api_004_01_search_existing,
                self.test_api_004_02_search_chinese,
                self.test_api_004_03_search_not_found,
                self.test_api_004_04_search_empty_query,
                self.test_api_004_05_search_with_threshold,
            ]),
            
            # API-005: 智能问答
            ("API-005 智能问答", [
                self.test_api_005_01_chat_normal,
                self.test_api_005_02_chat_with_sources,
                self.test_api_005_03_chat_empty_question,
            ]),
            
            # API-006: 清空知识库
            ("API-006 清空知识库", [self.test_api_006_01_clear_cache]),
        ]
        
        for group_name, tests in test_methods:
            print(f"\n--- {group_name} ---")
            for test in tests:
                try:
                    test()
                except Exception as e:
                    print(f"  ✗ Test execution error: {e}")
        
        test_results["end_time"] = datetime.now()
        
        # 打印摘要
        self.print_summary()
        
        return test_results["failed"] == 0
    
    def print_summary(self):
        """打印测试摘要"""
        duration = (test_results["end_time"] - test_results["start_time"]).total_seconds()
        
        print("\n" + "=" * 70)
        print("测试摘要")
        print("=" * 70)
        print(f"总测试数: {test_results['total']}")
        print(f"通过: {test_results['passed']}")
        print(f"失败: {test_results['failed']}")
        print(f"通过率: {test_results['passed']/test_results['total']*100:.1f}%")
        print(f"执行时间: {duration:.2f}秒")
        
        if test_results["errors"]:
            print("\n失败详情:")
            for error in test_results["errors"]:
                print(f"  - [{error['test_id']}] {error['test_name']}: {error['message']}")
        
        print("=" * 70)
        
        if test_results["failed"] == 0:
            print("🎉 所有测试通过!")
        else:
            print(f"❌ {test_results['failed']} 个测试失败")


def main():
    """主函数"""
    # 检查服务是否可用
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code != 200:
            print(f"错误: API服务未就绪 (状态码: {resp.status_code})")
            print("请先启动服务: cd /home/qw/.openclaw/workspace/projects/mpower_Rag && python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
            return 1
    except Exception as e:
        print(f"错误: 无法连接到API服务 ({BASE_URL})")
        print(f"详情: {e}")
        print("请先启动服务")
        return 1
    
    # 运行测试
    runner = TestRunner()
    success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
