@echo off
:: vehicle-test-agent GitHub仓库创建和推送脚本

echo ==========================================
echo vehicle-test-agent - GitHub仓库创建脚本
echo ==========================================

echo 请执行以下步骤创建GitHub仓库：

echo.
echo 1. 创建GitHub仓库
echo    - 访问 https://github.com/new
echo    - 仓库名称: vehicle-test-agent
echo    - 描述: 车载测试领域智能问答系统
echo    - 选择Public（推荐）或Private
echo    - 不要勾选'Initialize this repository with README'
echo.
echo 2. 配置Git远程仓库
echo    复制以下命令并执行：
echo.
echo git remote add origin https://github.com/YOUR_USERNAME/vehicle-test-agent.git
echo git push -u origin master
echo.
echo 3. 查看Git状态
git status

echo.
echo ==========================================
echo 脚本完成
echo ==========================================
echo.
echo ✓ 代码已提交到本地仓库
echo ⚠️  请手动完成上述步骤
echo.
echo 访问地址:
echo   - GitHub: https://github.com/YOUR_USERNAME/vehicle-test-agent
echo   - 文档: E:/workspace/mPower_Rag/README.md
echo   - 部署指南: E:/workspace/mPower_Rag/DEPLOYMENT.md
echo   - 项目总结: E:/workspace/mPower_Rag/PROJECT_SUMMARY.md

pause