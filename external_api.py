"""
外部API集成模块
支持从外部API获取文档和查询知识
"""
import logging
import httpx
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ExternalAPIClient:
    """外部API客户端"""

    def __init__(self, timeout: int = 30):
        """
        初始化外部API客户端

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def __del__(self):
        """析构函数，关闭客户端"""
        if hasattr(self, 'client'):
            self.client.close()

    def fetch_document(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        从外部API获取文档

        Args:
            url: API地址
            headers: 请求头
            params: 查询参数

        Returns:
            {
                'success': bool,
                'content': str,  # 文档内容
                'metadata': dict,  # 元数据
                'error': str  # 错误信息（如果失败）
            }
        """
        try:
            logger.info(f"Fetching document from external API: {url}")

            response = self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            # 尝试解析JSON响应
            try:
                data = response.json()

                # 假设API返回格式为: {"content": "...", "metadata": {...}}
                content = data.get('content', '')
                metadata = data.get('metadata', {})

                # 补充元数据
                metadata.update({
                    'source': 'external_api',
                    'url': url,
                    'status_code': response.status_code,
                })

                return {
                    'success': True,
                    'content': content,
                    'metadata': metadata,
                }

            except Exception as json_error:
                # 如果不是JSON，直接返回文本内容
                logger.warning(f"Response is not JSON, treating as plain text: {json_error}")
                content = response.text

                return {
                    'success': True,
                    'content': content,
                    'metadata': {
                        'source': 'external_api',
                        'url': url,
                        'status_code': response.status_code,
                        'format': 'text',
                    }
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching document: {e}")
            return {
                'success': False,
                'error': f"HTTP {e.response.status_code}: {str(e)}",
                'content': '',
                'metadata': {},
            }

        except httpx.RequestError as e:
            logger.error(f"Request error fetching document: {e}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'content': '',
                'metadata': {},
            }

        except Exception as e:
            logger.error(f"Unexpected error fetching document: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'content': '',
                'metadata': {},
            }

    def fetch_multiple_documents(
        self,
        urls: List[str],
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量获取文档

        Args:
            urls: API地址列表
            headers: 请求头
            params: 查询参数

        Returns:
            文档列表
        """
        results = []
        for url in urls:
            result = self.fetch_document(url, headers, params)
            results.append(result)

        return results

    def health_check(self, url: str) -> Dict[str, Any]:
        """
        检查外部API健康状态

        Args:
            url: API地址

        Returns:
            {
                'accessible': bool,
                'response_time_ms': int,
                'error': str  # 错误信息（如果失败）
            }
        """
        import time

        try:
            start_time = time.time()
            response = self.client.get(url, timeout=5)
            end_time = time.time()

            response_time_ms = int((end_time - start_time) * 1000)

            return {
                'accessible': response.status_code == 200,
                'response_time_ms': response_time_ms,
                'status_code': response.status_code,
            }

        except Exception as e:
            return {
                'accessible': False,
                'response_time_ms': 0,
                'error': str(e),
            }


class ExternalAPIAuth:
    """外部API认证管理"""

    @staticmethod
    def create_bearer_token(token: str) -> Dict[str, str]:
        """创建Bearer Token认证头"""
        return {
            'Authorization': f'Bearer {token}',
        }

    @staticmethod
    def create_api_key_header(api_key: str, header_name: str = 'X-API-Key') -> Dict[str, str]:
        """创建API Key认证头"""
        return {
            header_name: api_key,
        }

    @staticmethod
    def create_basic_auth(username: str, password: str) -> Dict[str, str]:
        """创建Basic认证头"""
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {
            'Authorization': f'Basic {credentials}',
        }


# 便捷函数
def fetch_from_external_api(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """便捷函数：从外部API获取文档"""
    client = ExternalAPIClient()
    try:
        return client.fetch_document(url, headers, params)
    finally:
        del client


def batch_fetch_from_external_api(
    urls: List[str],
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """便捷函数：批量从外部API获取文档"""
    client = ExternalAPIClient()
    try:
        return client.fetch_multiple_documents(urls, headers, params)
    finally:
        del client


if __name__ == "__main__":
    # 测试代码
    print("外部API客户端测试")

    # 测试健康检查
    client = ExternalAPIClient()
    result = client.health_check("https://httpbin.org/status/200")
    print(f"Health check result: {result}")
