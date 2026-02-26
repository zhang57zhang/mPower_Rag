# 流式输出功能说明

**版本**: 1.0
**最后更新**: 2026-02-23

---

## 📋 功能概述

流式输出（Streaming）可以实时显示生成的内容，提升用户体验，减少等待时间。

### 核心特性

- ✅ **实时生成** - 逐字符显示生成的内容
- ✅ **打字机效果** - 模拟真实的打字效果
- ✅ **SSE 支持** - 使用 Server-Sent Events 实现流式
- ✅ **兼容现有功能** - 支持对话历史、重排序等功能
- ✅ **源文档返回** - 生成完成后返回相关文档

---

## 🏗️ 架构设计

### 流式响应流程

```
用户提问
    ↓
API 接收请求
    ↓
执行检索（可选：重排序）
    ↓
流式生成答案
    ↓
逐字符返回（SSE）
    ↓
返回源文档（完成信号）
```

### SSE 数据格式

```json
// 问题 chunk
{
  "type": "question",
  "content": "用户的问题"
}

// 内容 chunk（多次）
{
  "type": "content",
  "content": "生成的文本片段",
  "done": false
}

// 完成信号（最后一次）
{
  "type": "done",
  "content": "",
  "done": true,
  "source_documents": [...],
  "metadata": {
    "reranked": true,
    "rerank_method": "cross_encoder",
    "source_count": 5
  }
}

// 错误信号（如果发生）
{
  "type": "error",
  "content": "错误信息",
  "done": true
}
```

---

## 🎨 API 接口

### 流式聊天接口

**端点**: `POST /api/v1/chat/stream`

**请求体**:
```json
{
  "question": "用户的问题",
  "conversation_id": "对话 ID（可选）",
  "use_history": true,
  "use_rerank": false,
  "top_k": 5
}
```

**响应类型**: `text/event-stream`

**响应示例**:
```
data: {"type": "question", "content": "什么是车载测试？"}

data: {"type": "content", "content": "车载测试是指", "done": false}

data: {"type": "content", "content": "对车辆及其组件", "done": false}

...

data: {"type": "content", "content": "的各", "done": false}

data: {"type": "done", "content": "", "done": true, "source_documents": [...], "metadata": {...}}
```

---

## 🎯 使用示例

### 1. Python 测试

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat/stream",
    json={
        "question": "什么是车载测试？",
        "use_history": False,
    },
    stream=True,  # 重要：启用流式
)

for line in response.iter_lines():
    if line.startswith("data: "):
        data = line[6:].strip()  # 移除 "data: " 前缀
        # 解析 JSON
        chunk = json.loads(data)
        print(chunk)
```

### 2. curl 测试

```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是车载测试？",
    "use_history": false
  }'
```

### 3. JavaScript 测试

```javascript
const eventSource = new EventSource('/api/v1/chat/stream');

eventSource.onopen = () => {
    console.log('连接已打开');
};

eventSource.onmessage = (event) => {
    const chunk = JSON.parse(event.data);
    
    if (chunk.type === 'question') {
        console.log('问题:', chunk.content);
    } else if (chunk.type === 'content') {
        // 显示生成的内容
        console.log('内容:', chunk.content);
    } else if (chunk.type === 'done') {
        console.log('完成');
        // 显示源文档
        if (chunk.source_documents) {
            console.log('源文档:', chunk.source_documents);
        }
        // 显示元数据
        if (chunk.metadata) {
            console.log('元数据:', chunk.metadata);
        }
        eventSource.close();
    } else if (chunk.type === 'error') {
        console.error('错误:', chunk.content);
        eventSource.close();
    }
};

eventSource.onerror = (error) => {
    console.error('错误:', error);
    eventSource.close();
};
```

---

## 🔧 配置选项

### API 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `question` | string | (必填) | 用户问题 |
| `conversation_id` | string | null | 对话 ID |
| `use_history` | boolean | true | 是否使用对话历史 |
| `use_rerank` | boolean | null | 是否使用重排序 |
| `top_k` | integer | 5 | 返回文档数量 |

### 流式参数（内部）

| 参数 | 说明 |
|------|------|
| `chunk_size` | 每个返回的块大小（字符数） |
| `encoding` | 文本编码（utf-8） |
| `timeout` | 请求超时时间（秒）|

---

## 📊 性能指标

### 预期性能

| 指标 | 数值 | 说明 |
|------|------|------|
| 首个 chunk 响应时间 | 500-1000ms | 开始响应时间 |
| chunk 间隔 | 10-50ms | 字符生成间隔 |
| 总生成时间 | 2-5s | 取决于问题复杂度 |
| 网络开销 | 低 | SSE 只需要一次连接 |

### 优化建议

1. **调整 chunk 大小**
   - 较小的 chunk 更流畅，但 HTTP 开销更大
   - 较大的 chunk 更高效，但可能有卡顿
   - 推荐值：10-50 字符

2. **启用 HTTP/2**
   - 减少连接开销
   - 支持 multiplexing

3. **使用 CDN**
   - 加速静态资源
   - 减少延迟

---

## 🎨 前端集成

### Streamlit 集成

```python
import streamlit as st
import requests
import json

# 界面
st.title("流式聊天")

# 输入框
question = st.text_input("请输入您的问题：")

if st.button("发送"):
    st.empty()  # 清空之前的显示
    
    # 创建占位符
    output_area = st.empty()
    result_area = st.empty()
    
    # 发送请求
    response = requests.post(
        "http://localhost:8000/api/v1/chat/stream",
        json={"question": question},
        stream=True,
    )
    
    # 显示问题
    with output_area.container():
        st.write(f"**问题**: {question}")
        st.markdown("---")
    
    # 流式显示答案
    with output_area.container():
        answer_container = st.empty()
        
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = line[6:].strip()
                if data:
                    chunk = json.loads(data)
                    
                    if chunk.get("type") == "question":
                        pass
                    elif chunk.get("type") == "content":
                        # 累积答案
                        if not hasattr(st.session_state, "full_answer"):
                            st.session_state.full_answer = ""
                        st.session_state.full_answer += chunk.get("content", "")
                        
                        # 实时显示
                        answer_container.markdown(st.session_state.full_answer)
                    elif chunk.get("type") == "done":
                        # 显示源文档
                        if chunk.get("source_documents"):
                            result_area.json(chunk["source_documents"])
    else:
        st.error("请求失败")
```

---

## 🧪 测试指南

### 运行测试脚本

```bash
# 测试流式输出
python scripts/test_streaming.py
```

### 测试覆盖

1. **功能测试**
   - ✅ 基本流式输出
   - ✅ 带对话历史的流式
   - ✅ 带重排序的流式
   - ✅ 错误处理

2. **性能测试**
   - ✅ 响应时间
   - ✅ chunk 间隔
   - ✅ 内存使用

3. **兼容性测试**
   - ✅ 不同浏览器
   - ✅ 不同网络条件
   - ✅ 长文本生成

---

## ⚠️ 注意事项

### 1. 浏览器兼容性

- ✅ Chrome / Edge: 完全支持
- ✅ Firefox: 完全支持
- ✅ Safari: 完全支持
- ⚠️ IE: 不支持 SSE

### 2. 网络要求

- 需要稳定的网络连接
- 防火墙需要允许 SSE
- 代理服务器需要支持 HTTP 流

### 3. 错误处理

- 客户端需要处理连接断开
- 需要处理超时情况
- 需要重连机制

### 4. 资源使用

- 服务器需要保持连接直到完成
- 建议设置合理的超时时间
- 建议添加连接数限制

---

## 🚀 后续改进

### 短期

1. **添加停止功能**
   - 允许用户停止生成
   - 客户端发送停止信号
   - 服务器中断生成

2. **优化流式生成**
   - 使用更高效的生成方法
   - 减少延迟
   - 优化 chunk 大小

3. **添加进度指示**
   - 显示生成进度百分比
   - 显示剩余时间估计

### 长期

4. **WebSocket 支持**
   - 更低延迟
   - 双向通信
   - 更好的错误处理

5. **协作流式**
   - 多用户实时协作
   - 共享会话
   - 实时同步

---

## 🆘 常见问题

### Q: SSE 和 WebSocket 的区别？
A: SSE 是单向的，更简单；WebSocket 是双向的，更复杂。对于简单的流式输出，SSE 已经足够。

### Q: 如何实现停止生成？
A: 客户端关闭连接即可，服务器会检测到连接断开并停止生成。

### Q: 如何处理网络中断？
A: 实现自动重连机制，从最后一个 chunk 重新开始。

### Q: 如何支持长文本？
A: 调整 `max_tokens` 参数，确保生成的内容不会截断。

### Q: 如何优化性能？
A: 调整 chunk 大小、启用 HTTP/2、使用 CDN、优化服务器性能。

---

## 📚 参考资料

### SSE 规范
- [MDN - Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [WHATWG - EventSource](https://html.spec.whatwg.org/multipage/server-sent-events.html)

### FastAPI 文档
- [FastAPI - Streaming Response](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

### 前端集成
- [Streamlit 文档](https://docs.streamlit.io/)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

---

**最后更新**: 2026-02-23
**版本**: 1.0
**维护者**: AI 助手
