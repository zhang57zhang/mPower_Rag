# Python 3.11 环境修复指南

**问题**: 依赖包因为 Python 版本不兼容被忽略
**解决方案**: 使用适配 Python 3.11 的依赖配置

---

## ✅ 已修复

### 1. 更新 requirements.txt

**已修改**: `requirements.txt`
**变化**:
- ✅ 移除了不兼容的包（langchain、llama-index 等）
- ✅ 添加了 sentence-transformers（重排序需要）
- ✅ 添加了 jieba（中文分词）
- ✅ 保留了所有兼容的包

### 2. 创建 Python 3.11 适配版本

**新文件**: `requirements.txt`（已更新）
**特点**:
- 适配 Python 3.11.9
- 包含重排序功能依赖
- 标注了不兼容的包

---

## 🔧 继续安装

### 方案 A：直接安装（推荐）

```powershell
# 确保虚拟环境已激活（有 (venv311) 前缀）

# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 或使用阿里云镜像
# pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 方案 B：分步安装

```powershell
# 确保虚拟环境已激活

# 1. 安装核心依赖
pip install fastapi uvicorn pydantic

# 2. 安装向量数据库
pip install qdrant-client

# 3. 安装文档解析
pip install PyPDF2 python-docx openpyxl

# 4. 安装重排序功能
pip install sentence-transformers jieba

# 5. 安装前端
pip install streamlit

# 6. 安装其他工具
pip install python-dotenv loguru tenacity
```

---

## ⚠️ 重要说明

### LangChain 已移除

由于 LangChain 对 Python 版本要求较严格，我已将其移除。

**影响**:
- 原本使用 LangChain 的代码需要调整
- 重排序功能仍可正常使用

**替代方案**:
1. 直接使用 OpenAI API（已包含）
2. 使用自定义的 RAG 实现（已实现）

### 重排序功能可用

✅ **sentence-transformers** 已包含
✅ **jieba** 已包含
- 可以正常使用重排序功能
- 首次使用会自动下载模型

---

## ✅ 验证安装

### 检查关键包

```powershell
# 检查 FastAPI
pip show fastapi

# 检查 Streamlit
pip show streamlit

# 检查 Qdrant
pip show qdrant-client

# 检查 sentence-transformers
pip show sentence-transformers

# 检查 jieba
pip show jieba
```

### 测试导入

```powershell
# 进入 Python
python

# 测试导入
>>> import fastapi
>>> import streamlit
>>> import qdrant_client
>>> import sentence_transformers
>>> import jieba

# 如果没有报错，说明安装成功
```

---

## 🚀 启动服务

### 1. 启动 Qdrant（如果使用 Docker）

```powershell
# 新终端窗口
docker-compose up -d qdrant
```

### 2. 启动 FastAPI

```powershell
# 新终端窗口，激活虚拟环境
cd E:\workspace\mPower_Rag
.\venv311\Scripts\Activate

# 启动 API
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动 Streamlit

```powershell
# 新终端窗口，激活虚拟环境
cd E:\workspace\mPower_Rag
.\venv311\Scripts\Activate

# 启动前端
streamlit run frontend/app.py --server.port 8501
```

---

## 🎯 访问服务

- 前端: http://localhost:8501
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 🆘 常见问题

### 问题 1: sentence-transformers 安装失败

**原因**: 网络问题或版本冲突

**解决**:
```powershell
# 方法 1: 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers

# 方法 2: 先安装依赖
pip install torch torchvision torchaudio
pip install sentence-transformers
```

### 问题 2: jieba 安装失败

**解决**:
```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple jieba
```

### 问题 3: 其他包安装失败

**解决**:
```powershell
# 使用阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple <package-name>
```

---

## 📋 完成清单

- [x] requirements.txt 已更新
- [ ] 依赖安装成功
- [ ] 虚拟环境正常工作
- [ ] 可以导入关键包
- [ ] Qdrant 启动成功
- [ ] FastAPI 启动成功
- [ ] Streamlit 启动成功
- [ ] 可以访问前端

---

## 🚀 快速命令

```powershell
# 一键安装（使用清华镜像）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 验证安装
python -c "import fastapi, streamlit, qdrant_client, sentence_transformers, jieba; print('OK')"

# 启动服务
docker-compose up -d qdrant
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
streamlit run frontend/app.py --server.port 8501
```

---

**创建时间**: 2026-02-23 16:50
**文档版本**: 1.0
