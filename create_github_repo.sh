#!/bin/bash
# GitHub仓库创建脚本

set -e

echo "=========================================="
echo "mPower_Rag - GitHub仓库创建脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}请执行以下步骤创建GitHub仓库：${NC}"
echo

echo "1. ${YELLOW}创建GitHub仓库${NC}"
echo "   - 访问 https://github.com/new"
echo "   - 仓库名称: mPower_Rag"
echo "   - 描述: 车载测试领域的RAG智能问答系统"
echo "   - 选择Public（推荐）或Private"
echo "   - 不要勾选'Initialize this repository with README'"
echo
echo "2. ${YELLOW}配置Git远程仓库${NC}"
echo "   复制以下命令并执行："
echo
echo "git remote add origin https://github.com/YOUR_USERNAME/mPower_Rag.git"
echo "git push -u origin master"
echo
echo "3. ${YELLOW}查看Git状态${NC}"
git status

echo ""
echo "=========================================="
echo "脚本完成"
echo "=========================================="
echo
echo -e "${GREEN}✓ 代码已提交到本地仓库${NC}"
echo -e "${YELLOW}⚠️  请手动完成上述步骤${NC}"
echo
echo "访问地址:"
echo "  - GitHub: https://github.com/YOUR_USERNAME/mPower_Rag"
echo "  - 文档: E:/workspace/mPower_Rag/README.md"
echo "  - 部署指南: E:/workspace/mPower_Rag/DEPLOYMENT.md"
echo "  - 项目总结: E:/workspace/mPower_Rag/PROJECT_SUMMARY.md"