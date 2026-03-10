# mPower_Rag 生产环境 Dockerfile
# 多阶段构建，优化镜像大小

# ==================== 构建阶段 ====================
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /build

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到临时目录
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==================== 生产阶段 ====================
FROM python:3.11-slim

# 设置标签
LABEL maintainer="mPower_Rag Team"
LABEL version="1.0.0"
LABEL description="mPower_Rag Production Image"

# 创建非 root 用户
RUN useradd -m -u 1000 appuser

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从构建阶段复制依赖
COPY --from=builder /install /usr/local

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p logs knowledge_base/documents knowledge_base/parsed models \
    && chown -R appuser:appuser logs knowledge_base models

# 切换到非 root 用户
USER appuser

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:${PATH}"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令（使用 gunicorn，生产环境推荐）
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
