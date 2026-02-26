# mPower_Rag 更新日志

## [未发布] - 2026-02-23

### 新增

#### 多轮对话管理 ✅
- ✅ 完整的对话管理模块（`src/core/conversation.py`）
  - 支持创建、获取、删除对话
  - 支持添加消息、获取对话历史
  - 自动限制历史记录数量
  - 对话元数据和上下文管理

#### API 接口
- ✅ `POST /api/v1/conversations` - 创建新对话
- ✅ `GET /api/v1/conversations/{id}` - 获取对话详情
- ✅ `POST /api/v1/conversations/{id}/messages` - 发送消息（支持多轮）
- ✅ `GET /api/v1/conversations` - 列出所有对话
- ✅ `DELETE /api/v1/conversations/{id}` - 删除对话

#### 前端功能
- ✅ 侧边栏对话历史面板
  - 新建对话按钮
  - 对话列表（显示 ID 和消息数量）
  - 对话切换功能
  - 对话删除功能
- ✅ 聊天风格的问答界面
  - 消息历史显示
  - 用户消息和助手消息区分样式
  - 示例问题快速提问
- ✅ 自动对话状态管理
  - 自动创建对话
  - 自动保存对话历史
  - session state 维护

#### 测试和工具
- ✅ `scripts/test_conversation.py` - 对话功能测试脚本
- ✅ `scripts/start_all.bat` - 一键启动所有服务
- ✅ `docs/CONVERSATION_INTEGRATION_REPORT.md` - 对话功能集成报告

### 改进

#### RAG 引擎
- 🔄 集成对话管理器
- 🔄 支持多轮对话（通过对话 ID 和历史上下文）
- 🔄 自动保存和加载对话历史
- 🔄 格式化历史消息为 LLM 可理解的格式

#### API 层
- 🔄 初始化对话管理器组件
- 🔄 在启动时自动初始化所有组件
- 🔄 添加对话管理相关的 Pydantic 模型

#### 文档
- 🔄 更新 `PROGRESS.md` - 对话管理完成
- 🔄 更新 `TODO.md` - 标记已完成的任务
- 🔄 更新 `README.md` - 添加新文档链接和最新进度

### 待办

#### 立即
- [ ] 测试对话功能（多轮对话、切换、删除）
- [ ] 配置 `LLM_API_KEY` 环境变量
- [ ] 启动服务并手动测试

#### 短期
- [ ] 集成重排序功能到检索流程
- [ ] 添加评估接口和仪表板
- [ ] 完善错误处理和日志

---

## [v0.1.0] - 2026-02-22

### 初始发布

#### 核心功能
- ✅ RAG 核心引擎（检索、增强、生成）
- ✅ 嵌入模型管理（OpenAI / HuggingFace）
- ✅ 向量数据库管理（Qdrant / Chroma）
- ✅ 文档加载与解析（PDF / DOCX / XLSX / TXT）
- ✅ FastAPI 后端接口
- ✅ Streamlit 前端应用

#### API 接口
- ✅ `POST /api/v1/chat` - 智能问答
- ✅ `GET /api/v1/search` - 文档搜索
- ✅ `POST /api/v1/documents/upload` - 上传文档
- ✅ `GET /api/v1/documents/stats` - 文档统计
- ✅ `GET /health` - 健康检查

#### 前端功能
- ✅ 智能问答模式
- ✅ 文档搜索模式
- ✅ 知识管理（上传文档）
- ✅ 示例问题快速提问
- ✅ 源文档显示

#### 部署
- ✅ Docker 支持
- ✅ Docker Compose 编排
- ✅ 环境变量配置
- ✅ 启动脚本（Windows / Linux）

#### 文档
- ✅ README.md
- ✅ PROGRESS.md
- ✅ TODO.md
- ✅ PROJECT_STATUS.md
- ✅ docs/QUICKSTART.md
- ✅ docs/RESUME.md

---

## 版本说明

### 版本编号规则
- **主版本号**：重大架构变更或不兼容更新
- **次版本号**：新功能添加或重要改进
- **修订号**：bug 修复或小改进

### 发布流程
1. 开发新功能
2. 编写测试
3. 更新文档
4. 提交 Pull Request
5. Code Review
6. 合并到主分支
7. 打标签发布
8. 更新 CHANGELOG.md

---

**最后更新**: 2026-02-23
