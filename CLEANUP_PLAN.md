# mPower_Rag 项目清理计划

**创建时间**: 2026-03-10
**目的**: 清理过程文件和非核心文件，保持项目整洁

---

## 📋 清理分类

### 🗑️ 需要删除的文件

#### 1. 过程文档（保留最终版本）
- [ ] AFTER_ENV_CONFIG_TODO.md - 环境配置待办（已完成）
- [ ] BUILD_REPORT.md - 构建报告（过程文档）
- [ ] CURRENT_TASK_REPORT.md - 任务报告（过程文档）
- [ ] DEPLOYMENT.md - 已被 docs/DEPLOYMENT_GUIDE.md 替代
- [ ] DOWNLOAD_GUIDE.md - 下载指南（已不需要）
- [ ] FILES_CHECKLIST.md - 文件检查清单（过程文档）
- [ ] GITHUB_COMMIT_REPORT.md - 提交报告（过程文档）
- [ ] OPTIMIZATION_PLAN.md, OPTIMIZATION_PLAN_V2.md - 保留 V3
- [ ] PROGRESS.md, PROGRESS_UPDATE.md - 进度文档（过程文档）
- [ ] PROJECT_STATUS.md, PROJECT_SUMMARY.md - 项目状态（已有 README）
- [ ] PYTHON_311_FIX_GUIDE.md, PYTHON_INSTALL_GUIDE.md, QUICK_INSTALL_GUIDE.md - 安装指南（已集成到部署指南）
- [ ] SERVICE_START_FAILURE_REPORT.md - 故障报告（过程文档）
- [ ] STEPS.md - 开发步骤（过程文档）
- [ ] WORK_COMPLETION_SUMMARY.md - 完成总结（过程文档）
- [ ] API_USAGE_GUIDE.md, ENHANCED_API_GUIDE.md - API 指南（已有更好的文档）

#### 2. 临时/调试文件
- [ ] debug_api_search.py - 调试脚本
- [ ] debug_rag.py - 调试脚本
- [ ] test_batch.txt, test_batch2.txt - 测试数据
- [ ] test_document.txt - 测试文档
- [ ] test_api.py - 根目录测试（已有 tests/）
- [ ] test_api_client.py - 测试客户端（已有 tests/）
- [ ] test_api_simple.py - 简单测试
- [ ] test_chinese_query.py - 中文测试
- [ ] test_local_vector.py - 向量测试
- [ ] test_new_features.py - 新功能测试
- [ ] test_phase2.py - 阶段测试
- [ ] test_query_only.py - 查询测试
- [ ] test_vector_search.py, test_vector_simple.py - 向量搜索测试

#### 3. 已集成的旧代码
- [ ] api_enhanced.py - 已集成到 src/api/main.py
- [ ] simple_api.py - 已集成到 src/api/main.py
- [ ] simple_rag_engine.py - 已集成到 src/core/rag_engine.py
- [ ] simple_config.py - 已集成到 config/settings.py
- [ ] document_manager.py - 已集成到 src/data/
- [ ] document_parser.py - 已集成到 src/data/
- [ ] external_api.py - 已集成到 src/api/
- [ ] vector_search.py - 已集成到 src/core/
- [ ] local_vector_store.py - 已集成到 src/core/
- [ ] memory_vector_store.py - 已集成到 src/core/

#### 4. 下载脚本（项目已完整）
- [ ] download_all.py
- [ ] download_from_github.py
- [ ] download_git.py
- [ ] download_qdrant.py, download_qdrant_binary.py
- [ ] download_sentence_transformers.py
- [ ] run_download_model.py

#### 5. 临时配置
- [ ] docker-compose.yml` - 异常文件名
- [ ] Dockerfile-requirements.txt - 临时文件
- [ ] install_deps.txt - 安装说明（已集成到文档）
- [ ] pip.conf - pip 配置（已不需要）

#### 6. 重复/旧版本脚本
- [ ] create_github_repo.sh - 创建仓库脚本（一次性）
- [ ] create_vehicle_test_agent_repo.bat - 创建仓库脚本（一次性）
- [ ] deploy.bat, deploy.sh - 被 deploy_prod.* 替代
- [ ] start_enhanced.bat, start_enhanced.sh - 启动脚本（已有更好的）
- [ ] startup_loader.py - 启动加载器（已不需要）
- [ ] health_check.py - 健康检查（已集成到 src/api/health.py）
- [ ] initialize_documents.py - 文档初始化（已集成）
- [ ] init_vector_store.py - 向量存储初始化（已集成）
- [ ] quick_start.py - 快速启动（已有更好的部署脚本）
- [ ] start_qdrant.py - Qdrant 启动（Docker 管理）
- [ ] run_tests.py - 测试运行器（使用 pytest）

#### 7. 其他
- [ ] TODO.md - 待办事项（已过时）

---

## ✅ 需要保留的核心文件

### 文档
- ✅ README.md - 项目主文档
- ✅ README.zh.md - 中文文档
- ✅ CHANGELOG.md - 变更日志
- ✅ RELEASE_CHECKLIST.md - 发布检查清单
- ✅ OPTIMIZATION_PLAN_V3.md - 最新优化计划
- ✅ LICENSE - 许可证

### 配置
- ✅ .env.example - 环境变量示例
- ✅ .env.production - 生产环境配置
- ✅ .env.development - 开发环境配置
- ✅ .gitignore - Git 忽略配置
- ✅ requirements.txt - Python 依赖
- ✅ prometheus.yml - Prometheus 配置

### Docker
- ✅ docker-compose.yml - Docker Compose 配置（开发）
- ✅ docker-compose.prod.yml - 生产环境配置
- ✅ Dockerfile - Docker 镜像构建

### 脚本
- ✅ deploy_prod.sh, deploy_prod.bat - 生产部署脚本
- ✅ test_api_prod.sh - API 测试脚本
- ✅ scripts/ - 脚本目录

### 核心代码
- ✅ src/ - 核心源码
- ✅ tests/ - 测试代码
- ✅ config/ - 配置文件
- ✅ docs/ - 文档目录
- ✅ frontend/ - 前端代码
- ✅ knowledge_base/ - 知识库
- ✅ k8s/ - Kubernetes 配置
- ✅ .github/ - GitHub 配置

---

## 📊 清理统计

- **待删除文件**: 60+ 个
- **预计释放空间**: ~500KB
- **保留核心文件**: ~30 个

---

## ⚠️ 注意事项

1. 删除前确认文件确实不需要
2. 重要文件先备份
3. 删除后测试项目仍能正常运行
4. 更新 .gitignore 防止再次添加

---

**执行前请确认**: 所有待删除文件都已检查，确认不影响项目功能
