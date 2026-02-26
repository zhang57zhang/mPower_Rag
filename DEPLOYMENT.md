# 部署指南

## 部署方式

### 方式1: Docker Compose（推荐）

#### 前置要求
- Docker 20.10+
- Docker Compose 2.0+

#### 部署步骤

**1. 准备配置文件**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入实际的配置
# 特别是设置LLM_API_KEY
nano .env
```

**2. 启动服务**

```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
deploy.bat
```

**3. 访问服务**

- API文档: http://localhost:8000/docs
- API健康: http://localhost:8000/health
- Qdrant: http://localhost:6333
- 前端界面: http://localhost:8501
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

#### 健康检查

```bash
# 运行健康检查脚本
python health_check.py
```

#### 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建
docker-compose build --no-cache
```

### 方式2: Kubernetes

#### 前置要求
- Kubernetes 1.20+
- kubectl
- Helm 3.x

#### 部署步骤

**1. 创建Namespace**

```bash
kubectl create namespace mpower-rag
```

**2. 部署Qdrant**

```bash
kubectl apply -f k8s/qdrant-deployment.yaml -n mpower-rag
```

**3. 部署API**

```bash
# 创建ConfigMap
kubectl create configmap mpower-rag-config \
  --from-literal=LLM_API_KEY=your_api_key \
  -n mpower-rag

# 部署应用
kubectl apply -f k8s/api-deployment.yaml -n mpower-rag
```

**4. 检查状态**

```bash
kubectl get pods -n mpower-rag
kubectl get services -n mpower-rag
```

### 方式3: 直接部署

#### 前置要求
- Python 3.14+
- Qdrant服务

#### 部署步骤

**1. 启动Qdrant**

```bash
# 使用Docker
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest

# 或使用下载的二进制文件
./qdrant.exe
```

**2. 安装依赖**

```bash
pip install -r requirements.txt
```

**3. 配置环境变量**

```bash
# Linux/Mac
export LLM_API_KEY=your_api_key
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# Windows (PowerShell)
$env:LLM_API_KEY="your_api_key"
$env:QDRANT_HOST="localhost"
$env:QDRANT_PORT="6333"
```

**4. 启动API**

```bash
python simple_api.py
```

## 环境变量

### 必需变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `LLM_API_KEY` | DeepSeek API密钥 | `sk-xxxxx` |

### 可选变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_BASE_URL` | LLM API地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | LLM模型名称 | `deepseek-chat` |
| `QDRANT_HOST` | Qdrant主机 | `localhost` |
| `QDRANT_PORT` | Qdrant端口 | `6333` |
| `API_PORT` | API端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `DEBUG` | 调试模式 | `false` |

## 监控

### Prometheus

访问: http://localhost:9090

**关键指标**:
- `http_requests_total` - 请求总数
- `http_request_duration_seconds` - 请求延迟
- `rag_search_duration_seconds` - 搜索耗时
- `rag_llm_duration_seconds` - LLM生成耗时

### Grafana

访问: http://localhost:3000
默认密码: `admin/admin`

**推荐仪表板**:
- API性能监控
- 系统资源监控
- 错误率监控

## 日志

### 日志位置

- **Docker**: `docker-compose logs`
- **直接部署**: `logs/` 目录

### 日志级别

- `DEBUG` - 详细调试信息
- `INFO` - 常规运行信息
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### 查看日志

```bash
# Docker Compose
docker-compose logs -f api

# 直接部署
tail -f logs/api.log
```

## 故障排查

### API无法启动

**检查**:
1. 端口8000是否被占用
2. LLM_API_KEY是否正确设置
3. Qdrant服务是否运行

**解决**:
```bash
# 检查端口
netstat -an | grep 8000

# 检查环境变量
echo $LLM_API_KEY

# 检查Qdrant
curl http://localhost:6333/health
```

### 检索无结果

**检查**:
1. 知识库是否有文档
2. 向量引擎是否初始化
3. 查询关键词是否正确

**解决**:
```bash
# 检查文档数量
curl http://localhost:8000/api/v1/documents/stats

# 检查健康状态
curl http://localhost:8000/health
```

### LLM调用失败

**检查**:
1. API密钥是否有效
2. 网络连接是否正常
3. API额度是否充足

**解决**:
```bash
# 测试API连接
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 性能优化

### 1. 向量检索优化

```bash
# 使用sentence-transformers提升准确率
pip install sentence-transformers

# 使用Qdrant实现持久化和加速
docker run -d -p 6333:6333 qdrant/qdrant:latest
```

### 2. 缓存优化

```python
# 在simple_config.py中启用缓存
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1小时
```

### 3. 并发优化

```bash
# 使用uvicorn多worker
uvicorn simple_api:app --workers 4 --host 0.0.0.0 --port 8000
```

## 安全建议

### 1. API密钥保护

- 使用环境变量存储密钥
- 不要将.env文件提交到Git
- 定期轮换API密钥

### 2. 网络安全

- 在生产环境中限制CORS
- 使用HTTPS/TLS
- 实施API认证
- 限制请求速率

### 3. 数据备份

```bash
# 备份Qdrant数据
docker cp mpower-rag-qdrant:/qdrant/storage ./backup

# 备份知识库
tar -czf knowledge_backup.tar.gz knowledge_base/
```

## 扩展

### 水平扩展

```bash
# 增加API实例
docker-compose up -d --scale api=3
```

### 垂直扩展

- 增加CPU和内存
- 使用SSD存储
- 优化数据库配置

---

**需要帮助？** 查看 `README.md` 或提交Issue。
