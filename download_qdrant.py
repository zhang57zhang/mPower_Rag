"""
下载Qdrant二进制文件
"""
import urllib.request
import urllib.error
import sys
from pathlib import Path
import time

def download_qdrant():
    """下载Qdrant"""
    print("=" * 60)
    print("下载 Qdrant 向量数据库")
    print("=" * 60)

    base_dir = Path(__file__).parent
    qdrant_exe = base_dir / "qdrant.exe"

    # 检查是否已存在
    if qdrant_exe.exists():
        print(f"✓ Qdrant已存在: {qdrant_exe}")
        return True

    # 下载URL
    url = "https://github.com/qdrant/qdrant/releases/latest/download/qdrant-windows-amd64.exe"

    print(f"\n下载地址: {url}")
    print(f"保存路径: {qdrant_exe}")
    print("\n开始下载... (这可能需要几分钟)")

    try:
        # 显示下载进度
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                mb_downloaded = downloaded / 1024 / 1024
                mb_total = total_size / 1024 / 1024
                print(f"\r进度: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')
            else:
                mb_downloaded = downloaded / 1024 / 1024
                print(f"\r已下载: {mb_downloaded:.1f} MB", end='')

        urllib.request.urlretrieve(url, qdrant_exe, show_progress)
        print("\n✓ 下载完成!")

        # 验证文件
        if qdrant_exe.exists() and qdrant_exe.stat().st_size > 1000000:
            print(f"✓ 文件验证成功 ({qdrant_exe.stat().st_size / 1024 / 1024:.1f} MB)")
            print("\n现在可以运行: python start_qdrant.py")
            return True
        else:
            print("✗ 下载的文件无效")
            return False

    except urllib.error.URLError as e:
        print(f"\n✗ 下载失败: {e}")
        print("\n请手动下载:")
        print(f"  1. 访问: {url}")
        print(f"  2. 保存到: {base_dir}")
        print(f"  3. 文件名: qdrant.exe")
        return False
    except Exception as e:
        print(f"\n✗ 下载失败: {e}")
        return False

if __name__ == "__main__":
    success = download_qdrant()
    sys.exit(0 if success else 1)
