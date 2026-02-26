# mPower_Rag 快速开始指南

## 目录

1. [环境准备](#环境准备)
2. [安装步骤](#安装步骤)
3. [配置说明](#配置说明)
4. [启动服务](#启动服务)
5. [使用指南](#使用指南)
6. [常见问题](#常见问题)

---

## 环境准备

### 必需软件

- **Python 3.10+**: [下载地址](https://www.python.org/downloads/)
- **Node.js 18+**: [下载地址](https://nodejs.org/)
- **Docker & Docker Compose** (可选，推荐): [下载地址](https://docs.docker.com/get-docker/)

### API 密钥

你需要一个 LLM API 密钥，支持以下提供商：

- **DeepSeek**: [申请地址](https://platform.deepseek.com/)
- **OpenAI**: [申请地址](https://platform.openai.com/)
- **其他兼容 OpenAI 的服务**: 按需配置

---

## 安装步骤

### 方式一：使用启动脚本（推荐）

#### Windows
```bash
cd mPower_Rag
scripts\setup.bat
```

#### Linux / macOS
```bash
cd mPower_Rag
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 方式二：手动安装

#### 1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

#### 4. 创建必要目录
```bash
mkdir -p knowledge_base/documents knowledge_base/parsed logs data/chroma
```

---

## 配置说明

编辑 `.env` 文件：

```bash
# LLM 配置（必填）
LLM_PROVIDER=deepseek  # 可选: openai, deepseek, qwen, glm
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com

# 向量数据库配置
VECTOR_DB_TYPE=qdrant  # qdrant 或 chroma
QDRANT_HOST=localhost
QDRANT_PORT=6333

# RAG 配置
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5

# 日志配置
LOG_LEVEL=INFO
```

### API 密钥配置

#### DeepSeek
```bash
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

#### OpenAI
```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo-preview
```

---

## 启动服务

### 方式一：使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务访问地址：
- 后端 API: http://localhost:8000
- 前端界面: http://localhost:8501
- Qdrant Dashboard: http://localhost:6333/dashboard

### 方式二：分别启动

#### 1. 启动 Qdrant（如果使用 Qdrant）
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

#### 2. 启动后端 API
```bash
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

python src/api/main.py
```

后端将在 http://localhost:8000 运行

#### 3. 启动前端界面
```bash
streamlit run frontend/app.py
```

前端将在 http://localhost:8501 运行

---

## 使用指南

### 1. 访问前端界面

打开浏览器访问: http://localhost:8501

### 2. 智能问答

- 在输入框中输入问题
- 点击"提交问题"
- 查看答案和相关文档

示例问题：
- "如何测试车载蓝牙模块的连接稳定性？"
- "车载 CAN 总线测试的标准流程是什么？"
- "如何诊断车载电源系统的故障？"

### 3. 文档搜索

- 切换到"文档搜索"标签
- 输入关键词搜索
- 查看相关文档和相似度

### 4. 上传文档

- 切换到"知识管理"标签
- 上传 PDF、DOCX、XLSX 或 TXT 文件
- 文档会自动处理并添加到知识库

### 5. API 调用

#### 问答接口
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "如何测试车载蓝牙模块？",
    "top_k": 5
  }'
```

#### 搜索接口
```bash
curl http://localhost:8000/api/v1/search?query=蓝牙测试&top_k=5
```

---

## 常见问题

### 1. 启动时提示 API Key 错误

**问题**: `openai_api_key not found`

**解决**:
- 检查 `.env` 文件是否存在
- 确保 `LLM_API_KEY` 已正确设置
- 重启服务

### 2. Qdrant 连接失败

**问题**: `Connection refused to Qdrant`

**解决**:
- 确认 Qdrant 服务正在运行: `docker ps | grep qdrant`
- 检查 `.env` 中的 `QDRANT_HOST` 和 `QDRANT_PORT` 配置
- 尝试使用 Chroma 代替 Qdrant: 设置 `VECTOR_DB_TYPE=chroma`

### 3. 嵌入模型加载失败

**问题**: `Failed to load embedding model`

**解决**:
- 检查网络连接
- 首次运行会下载模型，需要等待
- 可以使用本地模型替代

### 4. 文档上传失败

**问题**: `Failed to upload document`

**解决**:
- 检查文件格式是否支持（PDF, DOCX, XLSX, TXT）
- 确认 `knowledge_base/documents` 目录存在且有写入权限
- 查看后端日志获取详细错误信息

### 5. 查询返回结果为空

**问题**: `No relevant documents found`

**解决**:
- 确认知识库中已有文档
- 尝试降低 `TOP_K` 值
- 调整 `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 参数
- 使用"文档搜索"功能测试检索是否正常

### 6. 内存不足

**问题**: `Out of memory`

**解决**:
- 减小 `CHUNK_SIZE`
- 减少文档数量
- 增加系统内存或使用更大的机器

---

## 下一步

- 查看 [README.md](../README.md) 了解项目详情
- 查看 [STEPS.md](../STEPS.md) 了解开发进度
- 查看 [API 文档](./API.md) 了解接口详情
- 自定义配置参数优化性能

---

## 获取帮助

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 查看文档: [项目 Wiki](https://github.com/your-repo/wiki)
