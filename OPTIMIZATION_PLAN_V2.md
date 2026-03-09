# mPower_Rag 生产上线优化计划 v2.0

**创建时间**: 2026-03-10 00:15
**目标**: 优化到可上线发布状态

---

## 一、现状分析

### ✅ 已完成功能
- RAG 核心引擎（检索-增强-生成）
- 向量存储（Qdrant + 本地 TF-IDF fallback）
- 对话管理（多轮对话）
- 重排序（Cross-Encoder）
- 评估功能（RAG 评估指标）
- 缓存机制（Redis）
- 流式输出（SSE，需修复）
- 文档管理（多格式解析）

### ⚠️ 待优化问题

| 问题 | 严重程度 | 影响 |
|------|----------|------|
| CORS 配置 `allow_origins=["*"]` | 🔴 高 | 安全风险 |
| 无 API 认证机制 | 🔴 高 | 安全风险 |
| SSE 流式输出格式错误 | 🟡 中 | 功能异常 |
| 缺少 Rate Limiting | 🟡 中 | 资源滥用风险 |
| 健康检查不完整 | 🟡 中 | 监控盲区 |
| 缺少 Prometheus 指标 | 🟡 中 | 可观测性不足 |
| 测试覆盖率不足 | 🟡 中 | 质量保证 |
| Docker 镜像未优化 | 🟢 低 | 部署效率 |

---

## 二、优化任务清单

### Phase 1: 安全加固 (P0)

#### 1.1 API 认证
- [ ] 实现 API Key 认证中间件
- [ ] 支持 Bearer Token 认证
- [ ] 配置白名单路由（健康检查等）

#### 1.2 CORS 配置
- [ ] 收紧 CORS 配置，支持环境变量配置允许的域名
- [ ] 生产环境禁止 `*`

#### 1.3 输入验证
- [ ] 加强请求参数验证
- [ ] 防止 SQL 注入、XSS 攻击
- [ ] 文件上传大小和类型限制

#### 1.4 Rate Limiting
- [ ] 实现基于 IP/API Key 的限流
- [ ] 配置默认限制（如 100 req/min）

### Phase 2: 功能修复 (P0)

#### 2.1 流式输出修复
- [ ] 修复 SSE 格式（使用 `data: {...}\n\n` 格式）
- [ ] 实现真正的流式 token 输出
- [ ] 添加中断生成功能

### Phase 3: 性能优化 (P1)

#### 3.1 缓存优化
- [ ] 完善缓存策略（已有基础）
- [ ] 添加缓存预热
- [ ] 缓存命中率监控

#### 3.2 连接池
- [ ] HTTP 客户端连接池
- [ ] Redis 连接池
- [ ] Qdrant 连接池

#### 3.3 异步优化
- [ ] 并行检索多个数据源
- [ ] 异步文档处理

### Phase 4: 可观测性 (P1)

#### 4.1 监控指标
- [ ] Prometheus 指标暴露
- [ ] 请求延迟、错误率、QPS
- [ ] 缓存命中率
- [ ] 向量检索延迟

#### 4.2 日志优化
- [ ] 结构化日志（JSON）
- [ ] 请求 ID 追踪
- [ ] 敏感信息脱敏

#### 4.3 健康检查增强
- [ ] 检查 Redis 连接
- [ ] 检查 Qdrant 连接
- [ ] 检查 LLM API 可用性

### Phase 5: 质量保证 (P1)

#### 5.1 测试完善
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试
- [ ] 压力测试脚本

#### 5.2 文档完善
- [ ] API 文档更新
- [ ] 部署文档更新
- [ ] 配置说明

### Phase 6: 部署优化 (P2)

#### 6.1 Docker 优化
- [ ] 多阶段构建
- [ ] 最小化镜像大小
- [ ] 健康检查指令

#### 6.2 CI/CD
- [ ] GitHub Actions 配置
- [ ] 自动化测试
- [ ] 自动化部署

---

## 三、执行顺序

```
Phase 1 (安全) ──→ Phase 2 (修复) ──→ Phase 3 (性能)
                                              │
Phase 4 (监控) ←─────────────────────────────┘
      │
      ▼
Phase 5 (测试) ──→ Phase 6 (部署)
```

---

## 四、关键代码修改

### 4.1 API 认证中间件
```python
# src/api/middleware/auth.py
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### 4.2 SSE 流式输出修复
```python
async def generate_sse():
    async for token in stream_tokens():
        yield f"data: {json.dumps({'content': token})}\n\n"
    yield f"data: {json.dumps({'done': True})}\n\n"
```

### 4.3 Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat")
@limiter.limit("100/minute")
async def chat(request: Request, ...):
    ...
```

---

## 五、预期成果

| 指标 | 当前 | 目标 |
|------|------|------|
| 安全性 | 低（无认证） | 高（API Key + HTTPS） |
| 响应延迟 | ~2.5s | <1.5s（缓存命中） |
| 可用性 | 基础 | 99.9%（健康检查 + 重试） |
| 可观测性 | 低 | 高（Prometheus + 结构化日志） |
| 测试覆盖率 | ~30% | >80% |

---

## 六、时间估算

| Phase | 预计时间 |
|-------|----------|
| Phase 1 安全加固 | 2h |
| Phase 2 功能修复 | 1h |
| Phase 3 性能优化 | 2h |
| Phase 4 可观测性 | 1h |
| Phase 5 质量保证 | 2h |
| Phase 6 部署优化 | 1h |
| **总计** | **~9h** |

---

**最后更新**: 2026-03-10 00:15
