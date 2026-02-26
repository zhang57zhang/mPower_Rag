#!/usr/bin/env python3
"""
mPower_Rag 开发恢复脚本
读取 PROGRESS.md 并显示当前状态和下一步任务
"""
import sys
from pathlib import Path


def print_section(title: str, content: str = ""):
    """打印章节"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if content:
        print(content)


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    progress_file = project_root / "PROGRESS.md"
    todo_file = project_root / "TODO.md"

    if not progress_file.exists():
        print(f"❌ 进度文件不存在: {progress_file}")
        print("   请确保项目根目录存在 PROGRESS.md 文件")
        sys.exit(1)

    # 读取进度文件
    with open(progress_file, "r", encoding="utf-8") as f:
        progress_content = f.read()

    print_section("🚀 mPower_Rag 开发恢复")

    # 提取关键信息
    print_section("📊 总体进度")

    # 查找总体进度部分
    if "总体完成度" in progress_content:
        start = progress_content.find("总体完成度")
        end = progress_content.find("\n##", start)
        if end == -1:
            end = len(progress_content)
        print(progress_content[start:end].strip())

    # 提取待完成任务
    print_section("🔥 高优先级任务（下一步）")

    # 读取 TODO 文件的高优先级任务
    if todo_file.exists():
        with open(todo_file, "r", encoding="utf-8") as f:
            todo_content = f.read()

        # 提取高优先级部分
        if "## 🔴 高优先级任务" in todo_content:
            start = todo_content.find("## 🔴 高优先级任务")
            end = todo_content.find("\n## 🟡", start)
            if end == -1:
                end = todo_content.find("\n## 🟢", start)
            if end == -1:
                end = len(todo_content)
            print(todo_content[start:end].strip())

    print_section("📝 当前状态")

    # 提取当前状态信息
    if "## 🚧 当前正在开发" in progress_content:
        start = progress_content.find("## 🚧 当前正在开发")
        end = progress_content.find("\n## ⏳", start)
        if end == -1:
            end = len(progress_content)
        print(progress_content[start:end].strip())

    print_section("💡 重要提示")

    if "### 恢复开发时需要注意的事项" in progress_content:
        start = progress_content.find("### 恢复开发时需要注意的事项")
        end = progress_content.find("\n---\n", start)
        if end == -1:
            end = len(progress_content)
        print(progress_content[start:end].strip())

    print_section("🎯 建议的下一步行动")

    if "### 明天继续时需要做的事情" in progress_content:
        start = progress_content.find("### 明天继续时需要做的事情")
        end = progress_content.find("\n---\n", start)
        if end == -1:
            end = len(progress_content)
        print(progress_content[start:end].strip())

    print_section("✅ 准备就绪")

    print("""
现在你可以开始继续开发了！

快速检查清单：
  ☐ 确认 Python 环境正常
  ☐ 确认依赖已安装 (pip list)
  ☐ 确认 .env 配置正确
  ☐ 查看 logs/ 目录下的日志
  ☐ 运行测试确保基础功能正常

祝开发顺利！🚀
""")


if __name__ == "__main__":
    main()
