# mPower_Rag - 车载测试系统 RAG 构建步骤链

## 项目概述
构建一个车载测试系统的 RAG（检索增强生成）系统，最终供 AI+工程师前端使用。

## 步骤链设计

### Phase 1: 技术调研与选型
- [x] 搜索 RAG 相关 Skills
- [x] 识别候选 Skills:
  - wshobson/agents@rag-implementation (2.6K installs)
  - jeffallan/claude-skills@rag-architect (430 installs)
- [ ] 评估并安装合适的 RAG Skills
- [ ] 调研成熟 RAG 框架（LangChain, LlamaIndex, RAGAS）
- [ ] 调研向量数据库（Chroma, Pinecone, Weaviate, Qdrant）
- [ ] 设计项目技术栈

### Phase 2: 项目初始化
- [ ] 创建项目目录结构
- [ ] 配置开发环境
- [ ] 设置依赖管理
- [ ] 初始化版本控制

### Phase 3: 核心架构设计
- [ ] 设计车载测试数据模型
- [ ] 设计 RAG 流水线架构
- [ ] 设计 API 接口规范
- [ ] 设计前端交互流程

### Phase 4: 数据层构建
- [ ] 实现文档解析模块（PDF, DOCX, Excel 等）
- [ ] 实现文本分块策略
- [ ] 实现向量化集成
- [ ] 实现向量数据库管理
- [ ] 设计索引策略

### Phase 5: RAG 核心功能
- [ ] 实现检索模块（混合检索：关键词+语义）
- [ ] 实现重排序（Rerank）
- [ ] 集成 LLM（模型选择与调用）
- [ ] 实现上下文构建
- [ ] 实现答案生成

### Phase 6: 车载测试领域适配
- [ ] 构建车载测试知识库
- [ ] 实现测试用例检索
- [ ] 实现故障诊断支持
- [ ] 实现法规标准查询

### Phase 7: 前端接口层
- [ ] 设计 REST API 接口
- [ ] 实现 WebSocket 实时通信
- [ ] 实现流式输出
- [ ] 实现会话管理

### Phase 8: 质量保证
- [ ] 单元测试
- [ ] 集成测试
- [ ] RAG 评估（准确率、召回率）
- [ ] 性能测试

### Phase 9: 部署与运维
- [ ] 容器化（Docker）
- [ ] 部署配置
- [ ] 监控日志
- [ ] 文档编写

---

## 技术栈候选

### RAG 框架
- **LangChain** - 成熟，生态丰富，中文支持好
- **LlamaIndex** - 数据索引专业，适合文档密集型
- **RAGStack** - LangChain 官方 RAG 套件

### 向量数据库
- **Chroma** - 轻量级，易部署，适合原型
- **Qdrant** - 高性能，生产级，支持混合检索
- **Pinecone** - 托管服务，省运维

### LLM
- **DeepSeek** - 性价比高，中文优秀
- **GLM-4** - 清华出品，中文优化
- **Qwen** - 阿里开源，效果好

### 前端
- **Streamlit** - 快速原型，适合数据应用
- **Gradio** - 易用，适合 AI 原型
- **React + Next.js** - 生产级，灵活

---

## 当前状态
Phase 1 进行中：已完成 Skills 搜索，待评估安装
