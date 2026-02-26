#!/usr/bin/env python3
"""
mPower_Rag 环境检查脚本
验证开发环境是否正常
"""
import sys
from pathlib import Path
import subprocess


def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print(f"      需要 Python 3.10+")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n🔍 检查依赖包...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "streamlit",
        "qdrant-client",
        "pydantic",
        "python-dotenv",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n   缺少 {len(missing)} 个包: {', '.join(missing)}")
        print("   运行: pip install -r requirements.txt")
        return False

    return True


def check_env_file():
    """检查环境变量文件"""
    print("\n🔍 检查环境变量...")

    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        print("   ⚠️  .env 文件不存在")
        print("      运行: copy .env.example .env")
        return False

    # 检查关键配置
    import os
    from dotenv import load_dotenv

    load_dotenv(env_file)

    missing = []
    if not os.getenv("LLM_API_KEY"):
        missing.append("LLM_API_KEY")

    if missing:
        print(f"   ⚠️  缺少配置: {', '.join(missing)}")
        print("      请编辑 .env 文件并填入必要的配置")
        return False

    print("   ✅ .env 文件存在")
    print("   ✅ LLM_API_KEY 已配置")
    return True


def check_project_structure():
    """检查项目结构"""
    print("\n🔍 检查项目结构...")

    project_root = Path(__file__).parent.parent
    required_dirs = [
        "src/core",
        "src/data",
        "src/api",
        "config",
        "frontend",
        "docs",
    ]

    missing = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path}")
            missing.append(dir_path)

    if missing:
        return False

    return True


def check_services():
    """检查外部服务"""
    print("\n🔍 检查外部服务...")

    # 检查 Qdrant
    try:
        import qdrant_client
        client = qdrant_client.QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print("   ✅ Qdrant 可访问")
    except Exception as e:
        print(f"   ⚠️  Qdrant 不可访问: {e}")
        print("      运行: docker run -d -p 6333:6333 qdrant/qdrant")

    return True


def main():
    """主函数"""
    print("="*60)
    print("  mPower_Rag 环境检查")
    print("="*60)

    checks = [
        check_python_version,
        check_dependencies,
        check_env_file,
        check_project_structure,
        check_services,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n   ❌ 检查失败: {e}")
            results.append(False)

    print("\n" + "="*60)
    print("  检查结果")
    print("="*60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ 所有检查通过 ({passed}/{total})")
        print("\n🚀 环境就绪，可以开始开发了！")
        return 0
    else:
        print(f"⚠️  {total - passed} 项检查失败 ({passed}/{total})")
        print("\n请解决上述问题后再次运行此脚本")
        return 1


if __name__ == "__main__":
    sys.exit(main())
