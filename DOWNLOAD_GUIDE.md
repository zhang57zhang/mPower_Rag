# 下载依赖说明

## 快速开始

### 方法1: 使用自动下载脚本

```bash
# 检查当前状态
python download_all.py
# 选择选项 4 查看状态

# 下载Qdrant
python download_all.py
# 选择选项 1

# 下载sentence-transformers模型
python download_all.py
# 选择选项 2

# 下载所有
python download_all.py
# 选择选项 3
```

### 方法2: 单独运行下载脚本

```bash
# 下载Qdrant二进制
python download_qdrant_binary.py

# 下载sentence-transformers模型
python download_sentence_transformers.py

# 使用git方式下载
python download_git.py

# 从GitHub直接下载
python download_from_github.py
```

## 依赖项说明

### Qdrant（可选）

**用途**: 向量数据库，用于持久化存储和快速检索

**下载方式**:
- 自动: `python download_qdrant_binary.py`
- 手动: https://github.com/qdrant/qdrant/releases/latest/download/qdrant-windows-amd64.exe

**启动方式**:
```bash
# Windows
.\qdrant.exe

# 或使用Docker
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

**验证**:
```bash
curl http://localhost:6333/health
```

### sentence-transformers（可选）

**用途**: 高质量语义检索模型

**模型**: `paraphrase-multilingual-MiniLM-L12-v2` (~120MB)

**下载方式**:
- 自动: `python download_sentence_transformers.py`
- 方法1: 使用huggingface-cli（推荐）
- 方法2: 使用git lfs（需要git和git-lfs）

**安装git-lfs**:
```bash
git lfs install
```

**验证**:
```bash
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print('Model loaded successfully')"
```

## 替代方案

如果下载失败，系统会自动使用本地TF-IDF方案：

### 优点
- 零外部依赖
- 快速启动
- 支持中文检索

### 缺点
- 准确率较低（60-70% vs 80-90%）
- 语义理解有限

### 使用方式
```bash
# 直接启动API（会自动使用本地TF-IDF）
python simple_api.py
```

## 下载后配置

### 1. 启动Qdrant（如果已下载）

```bash
.\qdrant.exe
```

### 2. 初始化向量数据库（如果使用Qdrant）

```bash
python init_vector_store.py
```

### 3. 启动API服务

```bash
python simple_api.py
```

### 4. 测试API

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"蓝牙测试流程\"}"
```

## 故障排查

### Qdrant下载失败

**问题**: 网络连接超时
**解决方案**:
1. 手动下载: https://github.com/qdrant/qdrant/releases
2. 使用代理或VPN
3. 使用Docker: `docker run -p 6333:6333 qdrant/qdrant:latest`

### sentence-transformers模型下载失败

**问题**: HuggingFace无法访问
**解决方案**:
1. 安装huggingface-cli: `pip install huggingface-hub`
2. 使用git lfs克隆: `git lfs clone https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
3. 让系统自动下载（首次使用时）

### Git LFS问题

**问题**: git lfs未安装或配置错误
**解决方案**:
```bash
# 安装git-lfs
git lfs install

# 验证
git lfs version
```

## 推荐工作流程

### 快速启动（无需下载）
```bash
# 使用本地TF-IDF，零配置
python simple_api.py
```

### 标准配置（推荐）
```bash
# 下载sentence-transformers模型（更准确的语义检索）
python download_sentence_transformers.py

# 启动API
python simple_api.py
```

### 生产配置
```bash
# 下载所有依赖
python download_all.py
# 选择选项 3

# 启动Qdrant
.\qdrant.exe

# 初始化向量数据库
python init_vector_store.py

# 启动API
python simple_api.py
```

## 文件结构

下载后的文件结构：
```
E:\workspace\mPower_Rag\
├── qdrant.exe                    # Qdrant二进制文件
├── models\
│   └── paraphrase-multilingual-MiniLM-L12-v2\
│       ├── config.json            # 模型配置
│       ├── pytorch_model.bin      # 模型权重
│       ├── tokenizer.json         # 分词器
│       └── ...                   # 其他模型文件
├── download_all.py              # 主下载脚本
├── download_qdrant_binary.py   # Qdrant下载脚本
├── download_sentence_transformers.py  # 模型下载脚本
└── ...
```

## 性能对比

| 方案 | 启动时间 | 检索速度 | 准确率 | 外部依赖 |
|------|---------|---------|--------|---------|
| 本地TF-IDF | <1s | <10ms | 60-70% | 无 |
| sentence-transformers | 10-30s | <100ms | 80-90% | 模型文件 |
| Qdrant + sentence-transformers | 30-60s | <200ms | 85-95% | Qdrant + 模型 |

## 下一步

下载完成后，参考 `docs/QUICKSTART.md` 了解如何使用系统。

## 获取帮助

如有问题，检查：
1. `logs/` 目录下的日志文件
2. GitHub Issues: https://github.com/your-repo/issues
3. 文档: `README.md`

---

**注意**: 所有下载都是可选的。系统默认使用本地TF-IDF方案，可以立即使用。下载更多依赖可以提升检索质量。
