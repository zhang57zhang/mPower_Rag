# mPower_Rag - 车载测试RAG系统

## 项目概述

mPower_Rag是一个基于RAG（检索增强生成）技术的智能问答系统，专为车载测试领域设计。采用三层Fallback架构，确保系统在任何环境下都能稳定运行。

## 技术栈

- **后端**: FastAPI, Python 3.14+
- **向量检索**: Qdrant, sentence-transformers, TF-IDF
- **LLM**: DeepSeek API
- **前端**: Streamlit
- **部署**: Docker, Kubernetes
- **监控**: Prometheus, Grafana

## 核心特性

- ✅ 三层Fallback架构（零依赖到生产级）
- ✅ 智能混合检索策略
- ✅ 完整的API和Web界面
- ✅ Docker容器化部署
- ✅ 14个测试用例，100%通过

## 快速开始

```bash
# 零配置启动
python simple_api.py

# Docker部署
./deploy.sh
```

## 项目文件

- `README.md` - 详细项目文档
- `simple_api.py` - FastAPI服务
- `simple_rag_engine.py` - RAG引擎
- `Dockerfile` - Docker配置
- `docker-compose.yml` - 服务编排
- `tests/` - 测试套件

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License