# 对话功能快速开始

**版本**: 1.0
**日期**: 2026-02-23

---

## 🎯 适用场景

如果你想快速体验 mPower_Rag 的**多轮对话功能**，请按照以下步骤操作。

---

## 📋 准备工作

### 1. 确保环境就绪

```bash
# 检查 Python 版本
python --version  # 需要 3.10+

# 检查 Docker 是否运行
docker ps

# 安装依赖（如果还没有安装）
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `.env` 文件，设置 `LLM_API_KEY`：

```env
# LLM 配置
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-your-actual-api-key-here
LLM_BASE_URL=https://api.deepseek.com
```

**提示**：如果你使用 OpenAI，可以修改为：
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_API_KEY=sk-your-openai-key-here
LLM_BASE_URL=https://api.openai.com/v1
```

---

## 🚀 快速启动

### 一键启动（推荐）

```bash
scripts\start_all.bat
```

这会自动：
1. 启动 Qdrant 向量数据库
2. 启动 FastAPI 后端服务
3. 启动 Streamlit 前端服务

### 分步启动（如果需要调试）

```bash
# 终端 1：启动 Qdrant
docker-compose up -d qdrant

# 终端 2：启动 FastAPI
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 3：启动 Streamlit
streamlit run frontend/app.py --server.port 8501
```

---

## 💬 使用对话功能

### 1. 访问前端

打开浏览器，访问：
```
http://localhost:8501
```

### 2. 创建新对话

1. 在左侧边栏，点击 **"➕ 新建对话"**
2. 一个新的对话会被创建
3. 对话标题会显示 "对话 xxxxxx"（后 6 位 ID）

### 3. 开始对话

#### 方式 1：使用示例问题
- 点击任何示例问题按钮
- 系统会自动填充并发送问题

#### 方式 2：手动输入
- 在输入框中输入你的问题
- 点击 **"🚀 发送"** 按钮

**示例问题**：
- "什么是车载测试？"
- "车载 CAN 总线测试的标准流程是什么？"
- "如何诊断车载电源系统的故障？"

### 4. 多轮对话

继续提问，系统会记住之前的对话内容：

```
你：什么是车载测试？
助手：车载测试是指...

你：测试流程有哪些步骤？
助手：车载测试的流程包括...（参考了之前的对话）
```

### 5. 管理对话

#### 切换对话
- 在左侧边栏，点击任何对话
- 系统会切换到该对话

#### 删除对话
- 在左侧边栏，点击对话旁边的 🗑️ 按钮
- 确认删除

---

## 🧪 测试对话功能

### 自动化测试

运行测试脚本：

```bash
python scripts\test_conversation.py
```

这会自动测试：
- ✅ 创建对话
- ✅ 列出对话
- ✅ 获取对话详情
- ✅ 发送消息
- ✅ 多轮对话
- ✅ 删除对话

### API 测试

使用 `curl` 测试 API：

#### 创建对话
```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"test": true}}'
```

#### 发送消息
```bash
curl -X POST http://localhost:8000/api/v1/conversations/{conv_id}/messages \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是车载测试？",
    "top_k": 5,
    "use_history": true
  }'
```

#### 列出对话
```bash
curl http://localhost:8000/api/v1/conversations?limit=10
```

---

## 📊 API 文档

访问 Swagger UI 查看完整的 API 文档：

```
http://localhost:8000/docs
```

### 对话管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/conversations` | 创建新对话 |
| GET | `/api/v1/conversations/{id}` | 获取对话详情 |
| POST | `/api/v1/conversations/{id}/messages` | 发送消息 |
| GET | `/api/v1/conversations` | 列出所有对话 |
| DELETE | `/api/v1/conversations/{id}` | 删除对话 |

---

## 🔧 故障排除

### 问题 1：无法启动 Docker

**解决方案**：
1. 打开 Docker Desktop
2. 等待 Docker 完全启动
3. 重新运行启动脚本

### 问题 2：API Key 无效

**解决方案**：
1. 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确
2. 确认 API Key 还有余额
3. 检查 `LLM_BASE_URL` 是否正确

### 问题 3：无法访问前端

**解决方案**：
1. 检查 Streamlit 是否正在运行
2. 检查端口 8501 是否被占用
3. 尝试访问 http://127.0.0.1:8501

### 问题 4：答案质量差

**解决方案**：
1. 确保知识库中有相关文档
2. 尝试上传一些车载测试相关的文档
3. 调整 `top_k` 参数（在侧边栏）

### 问题 5：对话历史不保存

**解决方案**：
1. 检查是否创建了对话
2. 检查对话 ID 是否正确
3. 查看日志输出

---

## 📚 更多资源

### 文档
- `docs/CONVERSATION_INTEGRATION_REPORT.md` - 对话功能集成报告
- `PROGRESS.md` - 项目进度
- `README.md` - 项目说明

### 测试
- `scripts/test_conversation.py` - 测试脚本
- `tests/CONVERSATION_TEST_CHECKLIST.md` - 测试检查清单

### 恢复开发
如果需要继续开发，发送命令：
```
rag 继续
```

---

## 💡 提示

1. **首次使用**：先尝试示例问题，快速了解功能
2. **多轮对话**：连续提问可以获得更好的答案
3. **对话管理**：创建不同的对话来处理不同话题
4. **API 测试**：使用 `http://localhost:8000/docs` 进行 API 测试

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看日志输出（终端）
2. 检查 `docs/` 目录下的文档
3. 查看 `PROGRESS.md` 和 `TODO.md`

---

**祝使用愉快！** 🚗💬
