# mPower_Rag 项目文件清单

## 项目根目录文件

### 文档类
- `README.md` - 项目说明文档
- `STEPS.md` - 开发步骤链
- `PROJECT_STATUS.md` - 项目状态报告
- `BUILD_REPORT.md` - 构建完成报告
- `.gitignore` - Git 忽略配置

### 配置类
- `requirements.txt` - Python 依赖包
- `.env.example` - 环境变量模板
- `Dockerfile` - Docker 镜像配置
- `docker-compose.yml` - Docker Compose 编排配置

## 源代码目录 (src/)

### 核心模块 (src/core/)
- `embeddings.py` - 嵌入模型管理器
- `vector_store.py` - 向量数据库管理器（Qdrant/Chroma）
- `rag_engine.py` - RAG 核心引擎

### 数据层 (src/data/)
- `document_loader.py` - 文档加载和解析（PDF/DOCX/XLSX/TXT）

### API 层 (src/api/)
- `main.py` - FastAPI 主应用

### 待实现
- `models/` - 数据模型（空目录）
- `utils/` - 工具函数（空目录）

## 配置目录 (config/)
- `settings.py` - Pydantic 配置管理

## 前端目录 (frontend/)
- `app.py` - Streamlit 前端应用

## 文档目录 (docs/)
- `QUICKSTART.md` - 快速开始指南

## 脚本目录 (scripts/)
- `setup.bat` - Windows 启动脚本
- `setup.sh` - Linux/Mac 启动脚本

## 知识库目录 (knowledge_base/)
- （空，用于存放文档）

## 测试目录 (tests/)
- （空，待添加测试）

---

## 文件统计

| 类型 | 数量 |
|------|------|
| Python 源文件 | 5 |
| 配置文件 | 4 |
| 文档文件 | 5 |
| 脚本文件 | 2 |
| 空目录 | 4 |
| **总计** | **20** |

## 代码统计

| 文件 | 行数（约） |
|------|-----------|
| embeddings.py | ~70 |
| vector_store.py | ~180 |
| rag_engine.py | ~220 |
| document_loader.py | ~160 |
| main.py | ~250 |
| app.py | ~280 |
| settings.py | ~55 |
| **总计** | **~1215** |

---

## 功能模块

### ✅ 已实现
1. 嵌入模型管理（支持多种模型）
2. 向量数据库管理（Qdrant/Chroma）
3. 文档加载与解析（多格式支持）
4. RAG 核心引擎（检索-增强-生成）
5. RESTful API 接口
6. Streamlit 前端应用
7. Docker 部署配置
8. 跨平台启动脚本

### 🚧 待实现
1. 单元测试
2. 集成测试
3. RAG 评估指标
4. 用户认证
5. 流式输出优化
6. 缓存机制
7. 监控日志
8. 性能优化
