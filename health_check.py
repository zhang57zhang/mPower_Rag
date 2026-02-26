"""
健康检查脚本 - 检查所有服务状态
"""
import httpx
import sys
import time
from pathlib import Path

# 服务配置
SERVICES = {
    "API": {
        "url": "http://localhost:8000/health",
        "name": "mPower_Rag API",
        "timeout": 5
    },
    "Qdrant": {
        "url": "http://localhost:6333/health",
        "name": "Qdrant Vector DB",
        "timeout": 5
    },
    "Frontend": {
        "url": "http://localhost:8501",
        "name": "Streamlit Frontend",
        "timeout": 5
    },
    "Prometheus": {
        "url": "http://localhost:9090",
        "name": "Prometheus",
        "timeout": 5
    },
    "Grafana": {
        "url": "http://localhost:3000",
        "name": "Grafana",
        "timeout": 5
    }
}


def check_service(service_name: str, service_config: dict) -> dict:
    """检查单个服务状态"""
    try:
        start_time = time.time()
        response = httpx.get(
            service_config["url"],
            timeout=service_config["timeout"]
        )
        response_time = (time.time() - start_time) * 1000

        return {
            "name": service_config["name"],
            "status": "UP" if response.status_code == 200 else f"ERROR ({response.status_code})",
            "response_time": f"{response_time:.2f}ms",
            "url": service_config["url"]
        }
    except httpx.ConnectError:
        return {
            "name": service_config["name"],
            "status": "DOWN",
            "response_time": "N/A",
            "url": service_config["url"],
            "error": "Connection refused"
        }
    except httpx.TimeoutException:
        return {
            "name": service_config["name"],
            "status": "TIMEOUT",
            "response_time": "N/A",
            "url": service_config["url"],
            "error": "Request timeout"
        }
    except Exception as e:
        return {
            "name": service_config["name"],
            "status": "ERROR",
            "response_time": "N/A",
            "url": service_config["url"],
            "error": str(e)
        }


def main():
    """主函数"""
    print("=" * 60)
    print("mPower_Rag - 服务健康检查")
    print("=" * 60)
    print()

    results = {}

    # 检查所有服务
    for service_name, service_config in SERVICES.items():
        print(f"检查 {service_config['name']}...", end=" ")
        result = check_service(service_name, service_config)
        results[service_name] = result

        # 显示结果
        status_color = "OK" if result["status"] == "UP" else "ERROR"
        print(f"[{status_color}]")

    # 打印详细报告
    print("\n" + "=" * 60)
    print("详细报告")
    print("=" * 60)
    print()

    for service_name, result in results.items():
        print(f"{result['name']}:")
        print(f"  状态: {result['status']}")
        print(f"  URL: {result['url']}")
        print(f"  响应时间: {result['response_time']}")
        if "error" in result:
            print(f"  错误: {result['error']}")
        print()

    # 总结
    up_count = sum(1 for r in results.values() if r["status"] == "UP")
    total_count = len(results)

    print("=" * 60)
    print("总结")
    print("=" * 60)
    print(f"服务总数: {total_count}")
    print(f"运行中: {up_count}")
    print(f"停止/错误: {total_count - up_count}")
    print()

    # 返回状态码
    if up_count == total_count:
        print("所有服务运行正常!")
        return 0
    elif up_count > 0:
        print("部分服务运行中")
        return 1
    else:
        print("所有服务停止或错误")
        return 2


if __name__ == "__main__":
    sys.exit(main())
