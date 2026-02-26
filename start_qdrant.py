"""
启动Qdrant服务（Python方式）
使用qdrant-client内置的服务器
"""
import subprocess
import time
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def start_qdrant_server():
    """启动Qdrant服务器"""
    print("=" * 60)
    print("启动 Qdrant 向量数据库")
    print("=" * 60)

    # 检查Qdrant是否已经在运行
    try:
        import httpx
        response = httpx.get("http://localhost:6333/health", timeout=2)
        if response.status_code == 200:
            print("✓ Qdrant已经在运行")
            return True
    except:
        pass

    # 方法1: 尝试使用Docker
    print("\n尝试启动Qdrant...")

    # 方法2: 使用预编译的二进制文件
    qdrant_exe = Path(__file__).parent / "qdrant.exe"
    if qdrant_exe.exists():
        print(f"找到Qdrant二进制文件: {qdrant_exe}")
        try:
            process = subprocess.Popen(
                [str(qdrant_exe)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            print("✓ Qdrant进程已启动 (PID: {})".format(process.pid))

            # 等待服务就绪
            print("等待服务启动...")
            for i in range(30):
                try:
                    import httpx
                    response = httpx.get("http://localhost:6333/health", timeout=1)
                    if response.status_code == 200:
                        print(f"✓ Qdrant服务已就绪 (耗时 {i+1}秒)")
                        print(f"\nQdrant服务地址: http://localhost:6333")
                        print(f"Web UI: http://localhost:6333/dashboard\n")
                        return True
                except:
                    time.sleep(1)

            print("✗ Qdrant服务启动超时")
            process.terminate()
            return False

        except Exception as e:
            print(f"✗ 启动Qdrant失败: {e}")
            return False

    # 方法3: 提供手动启动指南
    print("\n未找到Qdrant二进制文件")
    print("\n请手动下载并启动Qdrant:")
    print("\n方法1 - 下载预编译版本:")
    print("  Windows: https://github.com/qdrant/qdrant/releases/latest/download/qdrant-windows-amd64.exe")
    print("  Linux:   https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu")
    print(f"  保存到: {Path(__file__).parent}")
    print("  运行: .\\qdrant.exe")
    print("\n方法2 - 使用Docker:")
    print("  docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest")
    print("\n方法3 - 使用Docker Compose:")
    print(f"  cd {Path(__file__).parent}")
    print("  docker-compose up -d qdrant")

    return False


if __name__ == "__main__":
    success = start_qdrant_server()
    sys.exit(0 if success else 1)
