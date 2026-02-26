# mPower_Rag 开发恢复指南

本指南用于恢复 mPower_Rag 项目的开发工作。

---

## 📋 恢复检查清单

### 1. 环境检查

在开始工作前，先确认开发环境正常：

```bash
# Windows
scripts\check.bat

# Linux/Mac
python scripts/check.py
```

所有检查应该通过 ✅。如果有失败，按照提示修复问题。

---

### 2. 查看进度

运行恢复脚本查看当前进度：

```bash
# Windows
scripts\resume.bat

# Linux/Mac
python scripts/resume.py
```

或手动查看以下文件：

1. **PROGRESS.md** - 详细进度记录
2. **TODO.md** - 待办任务清单
3. **PROJECT_STATUS.md** - 项目状态

---

### 3. 启动服务

确保所有服务正常运行：

```bash
# 使用 Docker Compose（推荐）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

或手动启动：

```bash
# 终端 1: 启动 Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# 终端 2: 启动后端 API
python src/api/main.py

# 终端 3: 启动前端
streamlit run frontend/app.py
```

---

### 4. 验证功能

访问以下地址验证服务正常：

- **前端**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **Qdrant 控制台**: http://localhost:6333/dashboard

测试基本功能：
- 上传一个测试文档
- 提问一个问题
- 搜索关键词

---

## 🎯 当前优先级任务

根据 `TODO.md`，当前的高优先级任务是：

### 1. 对话管理集成
- 修改 `src/core/rag_engine.py` 添加对话支持
- 在 `src/api/main.py` 添加对话相关接口
- 更新 `frontend/app.py` 支持多轮对话

### 2. 重排序集成
- 在检索流程中添加重排序步骤
- 添加配置选项
- 测试重排序效果

### 3. 评估功能
- 创建评估数据集
- 添加评估 API 接口
- 创建评估仪表板

---

## 📝 开发工作流

### 步骤 1: 选择任务
从 `TODO.md` 选择一个高优先级任务。

### 步骤 2: 理解需求
阅读相关代码，理解当前实现：
- 查看现有模块
- 理解代码结构
- 确定修改点

### 步骤 3: 开发功能
按照 TDD（测试驱动开发）方式：
1. 编写测试（如果适用）
2. 实现功能
3. 运行测试
4. 修复问题

### 步骤 4: 验证功能
- 手动测试新功能
- 检查错误处理
- 检查日志输出

### 步骤 5: 更新文档
- 更新 API 文档
- 更新 README
- 更新 PROGRESS.md（如果完成重要功能）

### 步骤 6: 提交代码
```bash
git add .
git commit -m "feat: 添加功能描述"
git push
```

---

## 🔄 持续集成

### 定期检查
每天开始时运行：

```bash
# 环境检查
scripts/check.py

# 查看进度
scripts/resume.py

# 启动服务
docker-compose up -d
```

### 每日更新
每天结束时：
1. 完成的任务在 `TODO.md` 中标记 [x]
2. 在 `PROGRESS.md` 中记录重要进展
3. 提交代码到版本库
4. 更新文档

---

## 🚨 常见问题

### 问题 1: 服务启动失败

**症状**: `docker-compose up` 失败

**解决**:
```bash
# 检查 Docker 状态
docker ps

# 查看详细日志
docker-compose logs api

# 重启服务
docker-compose restart api
```

### 问题 2: API 调用失败

**症状**: 前端无法连接后端

**解决**:
```bash
# 检查 API 是否运行
curl http://localhost:8000/health

# 检查端口占用
netstat -ano | findstr :8000

# 查看后端日志
docker-compose logs -f api
```

### 问题 3: Qdrant 连接失败

**症状**: 无法连接向量数据库

**解决**:
```bash
# 检查 Qdrant 是否运行
curl http://localhost:6333/

# 重启 Qdrant
docker-compose restart qdrant

# 或使用 Chroma 代替
# 修改 .env: VECTOR_DB_TYPE=chroma
```

### 问题 4: LLM API 错误

**症状**: `openai_api_key not found`

**解决**:
```bash
# 检查 .env 文件
cat .env | grep LLM_API_KEY

# 确保 LLM_API_KEY 已设置
# 重启服务
docker-compose restart api
```

### 问题 5: 依赖问题

**症状**: `ImportError: No module named 'xxx'`

**解决**:
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或在 Docker 中重新构建
docker-compose build api
docker-compose up -d api
```

---

## 📞 获取帮助

### 文档资源
- [README.md](../README.md) - 项目总览
- [QUICKSTART.md](../docs/QUICKSTART.md) - 快速开始
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - 项目状态
- [API 文档](http://localhost:8000/docs) - 在线 API 文档

### 日志位置
- 应用日志: `logs/app.log`
- Docker 日志: `docker-compose logs [service]`
- 前端日志: 控制台输出

---

## ✅ 恢复完成清单

在确认可以开始开发前，确认：

- [ ] Python 环境正常 (check.py 通过)
- [ ] 所有依赖已安装
- [ ] .env 配置正确
- [ ] 所有服务正常运行
- [ ] 基本功能测试通过
- [ ] 已查看 PROGRESS.md 和 TODO.md
- [ ] 已选择下一个任务
- [ ] 理解当前代码结构

---

## 🎓 开发提示

### 代码质量
- 保持代码整洁
- 添加类型注解
- 编写文档字符串
- 添加日志记录

### 测试
- 编写单元测试
- 集成测试重要功能
- 测试错误处理

### 文档
- 及时更新文档
- 添加使用示例
- 记录重要决策

---

**祝你开发顺利！🚀**

有问题随时查看相关文档或联系支持。
