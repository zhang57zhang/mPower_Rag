# mPower_Rag 生产环境部署指南

**版本**: 1.0.0  
**更新时间**: 2026-03-10  
**适用环境**: Linux, Windows, macOS

---

## 📋 部署前准备

### 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB | 50GB+ SSD |
| 操作系统 | Linux/Windows/macOS | Ubuntu 20.04+ |

### 软件依赖

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.0+
- **curl**: 用于健康检查

### 网络要求

- 端口 8000: API 服务
- 端口 6333-6334: Qdrant
- 端口 6379: Redis
- 端口 9090: Prometheus（可选）
- 端口 3000: Grafana（可选）

---

## 🚀 快速部署

### 1. 获取代码

```bash
git clone https://github.com/your-username/mPower_Rag.git
cd mPower_Rag
```

### 2. 配置环境变量

```bash
# 复制生产环境配置模板
cp .env.production .env

# 编辑配置文件
nano .env
```

**必须配置的项：**

```bash
# LLM API Key（必需）
LLM_API_KEY=your_actual_deepseek_api_key

# API 认证密钥（必需）
API_KEYS=your_secure_api_key_1,your_secure_api_key_2
ADMIN_API_KEYS=your_admin_api_key

# CORS 允许的域名（必需）
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

**生成安全的 API Key：**

```bash
# 生成随机 API Key
openssl rand -hex 32
```

### 3. 执行部署

**Linux/macOS:**

```bash
chmod +x deploy_prod.sh
./deploy_prod.sh
```

**Windows:**

```cmd
deploy_prod.bat
```

### 4. 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# API 测试（需要 API Key）
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"query": "蓝牙测试流程"}'
```

---

## 📊 监控配置

### Prometheus 监控

访问: http://localhost:9090

关键指标：
- `http_requests_total`: HTTP 请求总数
- `http_request_duration_seconds`: 请求延迟
- `rag_queries_total`: RAG 查询总数
- `llm_calls_total`: LLM 调用次数
- `cache_hits_total`: 缓存命中数

### Grafana 仪表板

访问: http://localhost:3000  
默认账号: admin / admin（首次登录需修改）

**推荐仪表板：**
1. 导入预配置仪表板: `monitoring/grafana/dashboards/`
2. 或手动创建仪表板

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f api

# 查看最近 100 行日志
docker-compose -f docker-compose.prod.yml logs --tail=100 api
```

---

## 🔐 安全配置

### 1. API 认证

**生成 API Key:**

```python
import secrets
print(f"mpower_{secrets.token_urlsafe(32)}")
```

**配置:**

```bash
# .env
API_AUTH_ENABLED=true
API_KEYS=key1,key2,key3
ADMIN_API_KEYS=admin_key1
```

**使用:**

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/v1/chat
```

### 2. CORS 配置

```bash
# 生产环境必须设置具体域名
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com

# 不要使用 * 或空值
```

### 3. 限流配置

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST_SIZE=20
```

### 4. HTTPS 配置（推荐）

**使用 Nginx 反向代理：**

```nginx
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔄 备份与恢复

### 自动备份

**创建定时任务:**

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点备份
0 2 * * * /path/to/mPower_Rag/scripts/backup.sh
```

### 手动备份

```bash
# 执行备份
./scripts/backup.sh

# 备份文件位置
# backups/qdrant/backup_YYYYMMDD_HHMMSS.tar.gz
# backups/redis/backup_YYYYMMDD_HHMMSS.rdb
```

### 恢复数据

```bash
# 恢复 Qdrant
./scripts/restore.sh backups/qdrant/backup_20260310_020000.tar.gz

# 恢复 Redis
./scripts/restore_redis.sh backups/redis/backup_20260310_020000.rdb
```

---

## 📈 性能优化

### 1. 资源配置

**docker-compose.prod.yml:**

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 2. 缓存优化

```bash
# .env
CACHE_ENABLED=true
CACHE_TTL=3600  # 1小时
REDIS_MAXMEMORY=512mb
```

### 3. 并发配置

```bash
# .env
WORKERS=4  # 建议 CPU 核心数 * 2 + 1
```

### 4. 数据库优化

**Qdrant 配置:**

```yaml
environment:
  - QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS=4
  - QDRANT__STORAGE__PERFORMANCE__MAX_OPTIMIZATION_THREADS=2
```

---

## 🛠️ 运维操作

### 启动服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

### 重启服务

```bash
docker-compose -f docker-compose.prod.yml restart api
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker-compose -f docker-compose.prod.yml up -d --build
```

### 查看状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 进入容器

```bash
# 进入 API 容器
docker exec -it mpower-rag-api bash

# 进入 Redis 容器
docker exec -it mpower-rag-redis redis-cli
```

---

## 🔍 故障排查

### 常见问题

#### 1. API 启动失败

**检查日志:**

```bash
docker-compose -f docker-compose.prod.yml logs api
```

**可能原因:**
- 环境变量未配置
- Qdrant 未启动
- 端口被占用

#### 2. 健康检查失败

**检查依赖服务:**

```bash
# Qdrant
curl http://localhost:6333/health

# Redis
docker exec mpower-rag-redis redis-cli ping
```

#### 3. 性能问题

**检查资源使用:**

```bash
docker stats
```

**检查慢查询:**

```bash
tail -f logs/app.log | grep "slow"
```

#### 4. 内存泄漏

**监控内存:**

```bash
docker stats --no-stream
```

**重启服务:**

```bash
docker-compose -f docker-compose.prod.yml restart api
```

---

## 📞 支持

- **文档**: [README.md](../README.md)
- **问题**: [GitHub Issues](https://github.com/your-username/mPower_Rag/issues)
- **社区**: [Discord](https://discord.com/invite/clawd)

---

## ✅ 部署检查清单

部署前请确认：

- [ ] 服务器满足系统要求
- [ ] Docker 和 Docker Compose 已安装
- [ ] .env 文件已正确配置
- [ ] LLM_API_KEY 已配置
- [ ] API_KEYS 已生成并配置
- [ ] CORS_ORIGINS 已设置为实际域名
- [ ] 防火墙已开放必要端口
- [ ] 域名已解析到服务器
- [ ] SSL 证书已配置（如使用 HTTPS）
- [ ] 备份策略已规划
- [ ] 监控告警已配置

部署后请验证：

- [ ] 所有服务容器正常运行
- [ ] 健康检查返回 healthy
- [ ] API 接口可以正常调用
- [ ] 认证机制工作正常
- [ ] 监控指标正常采集
- [ ] 日志正常输出
- [ ] 备份脚本可正常执行

---

**最后更新**: 2026-03-10
