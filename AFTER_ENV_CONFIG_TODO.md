# 环境配置完成后待办清单

**创建时间**: 2026-02-23 09:23
**状态**: 等待环境配置完成

---

## 📋 前提条件

在开始以下任务之前，请确保：

- [ ] Python 3.10 或 3.11 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖包已安装（`pip install -r requirements.txt`）
- [ ] `.env` 文件已配置（包括 `LLM_API_KEY`）
- [ ] Docker 已启动（用于 Qdrant）

---

## 🚀 启动服务（5-10 分钟）

### 1. 启动 Qdrant 向量数据库
```bash
cd mPower_Rag
docker-compose up -d qdrant
```

**验证**:
```bash
# 检查 Qdrant 是否运行
curl http://localhost:6333/collections

# 或访问管理界面
# http://localhost:6333/dashboard
```

### 2. 启动 FastAPI 后端服务
```bash
cd mPower_Rag
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**验证**:
```bash
# 健康检查
curl http://localhost:8000/health

# 访问 API 文档
# http://localhost:8000/docs
```

### 3. 启动 Streamlit 前端服务
```bash
cd mPower_Rag
streamlit run frontend/app.py --server.port 8501
```

**验证**:
```
# 访问前端界面
# http://localhost:8501
```

### 4. 一键启动（可选）
```bash
scripts\start_all.bat
```

---

## 🧪 测试对话功能（10-15 分钟）

### 手动测试

#### 测试 1: 创建对话
1. 访问 http://localhost:8501
2. 点击左侧边栏的 "➕ 新建对话"
3. 验证对话 ID 显示在标题中
4. 验证侧边栏显示新对话

#### 测试 2: 发送消息
1. 输入问题："什么是车载测试？"
2. 点击 "🚀 发送"
3. 等待答案生成
4. 验证答案显示
5. 验证源文档显示（如果有知识库内容）

#### 测试 3: 多轮对话
1. 继续提问："测试流程有哪些步骤？"
2. 验证答案参考了之前的对话
3. 验证对话历史正确显示

#### 测试 4: 对话切换
1. 点击 "➕ 新建对话" 创建第二个对话
2. 在新对话中提问
3. 点击侧边栏的第一个对话
4. 验证切换回第一个对话

#### 测试 5: 删除对话
1. 选中一个对话
2. 点击对话旁边的 🗑️ 按钮
3. 验证对话已删除

### 自动化测试

运行测试脚本：
```bash
python scripts\test_conversation.py
```

**预期输出**:
- ✅ 测试 1: 创建对话 - 通过
- ✅ 测试 2: 列出对话 - 通过
- ✅ 测试 3: 获取对话详情 - 通过
- ✅ 测试 4: 发送消息 - 通过
- ✅ 测试 5: 多轮对话 - 通过
- ✅ 测试 6: 删除对话 - 通过

---

## 📊 测试检查清单

使用 `tests/CONVERSATION_TEST_CHECKLIST.md` 进行系统化测试：

- [ ] 环境检查
  - [ ] Python 版本正确
  - [ ] 依赖已安装
  - [ ] 配置文件已设置
  - [ ] Docker 已启动

- [ ] 服务启动
  - [ ] Qdrant 已启动
  - [ ] FastAPI 已启动
  - [ ] Streamlit 已启动

- [ ] 手动测试
  - [ ] 创建对话
  - [ ] 发送消息
  - [ ] 多轮对话
  - [ ] 对话切换
  - [ ] 删除对话

- [ ] 自动化测试
  - [ ] 测试脚本运行成功
  - [ ] 所有测试通过

- [ ] 功能验收
  - [ ] 可以创建对话
  - [ ] 可以发送消息并获取答案
  - [ ] 多轮对话正常工作
  - [ ] 可以切换对话
  - [ ] 可以删除对话

- [ ] 性能验收
  - [ ] 创建对话响应时间 < 1 秒
  - [ ] 发送消息响应时间 < 10 秒
  - [ ] 前端界面流畅

- [ ] 用户体验验收
  - [ ] 界面美观
  - [ ] 操作直观
  - [ ] 错误提示清晰

---

## 📝 测试结果记录

### 成功的测试

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 创建对话 | ⬜ 通过 / ❌ 失败 | |
| 发送消息 | ⬜ 通过 / ❌ 失败 | |
| 多轮对话 | ⬜ 通过 / ❌ 失败 | |
| 对话切换 | ⬜ 通过 / ❌ 失败 | |
| 删除对话 | ⬜ 通过 / ❌ 失败 | |
| 自动化测试 | ⬜ 通过 / ❌ 失败 | |

### 遇到的问题

1.
2.
3.

### 解决方案

1.
2.
3.

---

## 🎯 环境配置完成后下一步

### 如果测试全部通过 ✅

恭喜！对话管理功能已成功集成。

**下一步**：

1. **上传测试文档**
   - 访问 "📁 知识管理" 模式
   - 上传一些车载测试相关的文档（PDF、DOCX、TXT）
   - 验证文档被正确解析和向量化

2. **测试完整的 RAG 流程**
   - 在"💬 智能问答"模式中提问
   - 验证答案基于知识库内容
   - 验证源文档引用准确

3. **集成重排序功能**
   - 修改检索流程，添加重排序步骤
   - 添加配置选项
   - 性能测试

4. **添加评估功能**
   - 创建评估数据集
   - 添加评估 API 接口
   - 创建评估仪表板

### 如果测试失败 ❌

**参考文档**：

1. 查看 `SERVICE_START_FAILURE_REPORT.md` 了解常见问题
2. 查看 `tests/CONVERSATION_TEST_CHECKLIST.md` 进行系统化排查
3. 查看日志输出（终端）
4. 查看浏览器控制台（前端错误）

**调试步骤**：

1. 检查所有服务是否正常运行
2. 检查端口是否被占用
3. 检查 API Key 是否有效
4. 检查网络连接
5. 查看详细的错误日志

---

## 📚 相关文档

### 快速开始
- `docs/CONVERSATION_QUICKSTART.md` - 对话功能快速开始

### 功能文档
- `docs/CONVERSATION_INTEGRATION_REPORT.md` - 对话功能集成报告
- `docs/CONVERSATION_FEATURES.md` - 对话功能详细说明（待创建）

### 测试文档
- `tests/CONVERSATION_TEST_CHECKLIST.md` - 测试检查清单
- `scripts/test_conversation.py` - 自动化测试脚本

### 项目文档
- `PROGRESS.md` - 项目进度
- `TODO.md` - 待办事项
- `README.md` - 项目说明

### 问题排查
- `SERVICE_START_FAILURE_REPORT.md` - 服务启动失败报告

---

## 🆘 需要帮助？

如果遇到问题：

1. **查看日志**
   - FastAPI 日志：启动 FastAPI 的终端
   - Streamlit 日志：启动 Streamlit 的终端
   - Qdrant 日志：`docker logs qdrant`

2. **访问 API 文档**
   - http://localhost:8000/docs

3. **使用测试脚本**
   ```bash
   python scripts\test_conversation.py
   ```

4. **检查文档**
   - 查看 `docs/` 目录下的文档
   - 查看 `SERVICE_START_FAILURE_REPORT.md`

---

## 📞 反馈

测试完成后，请记录：

- 测试结果：✅ 通过 / ❌ 失败
- 遇到的问题：
- 改进建议：

---

**生成时间**: 2026-02-23 09:23
**预计完成时间**: 20-30 分钟
**下次更新**: 环境配置完成后
