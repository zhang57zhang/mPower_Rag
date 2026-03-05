# mPower_Rag 增强版 - API使用指南

## 🎯 新增功能

### 1. 文档管理
- ✅ 支持多种文档格式（txt/md/docx/xlsx/pdf）
- ✅ 文档上传、删除、列表、查询
- ✅ 文档分类管理
- ✅ 元数据管理

### 2. 外部API调用
- ✅ 标准化查询接口
- ✅ 批量查询支持
- ✅ 文档管理API
- ✅ RESTful设计

---

## 🚀 快速启动

### 方式1: Windows
```bash
cd mPower_Rag
start_enhanced.bat
```

### 方式2: Linux/Mac
```bash
cd mPower_Rag
bash start_enhanced.sh
```

### 方式3: 手动启动
```bash
cd mPower_Rag
python api_enhanced.py
```

---

## 📚 API文档

### 访问地址
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📖 核心接口

### 1. 文档管理

#### 1.1 上传文档（文件上传）

**接口**: `POST /api/v1/documents/upload`

**请求**:
- Content-Type: `multipart/form-data`
- 参数:
  - `file`: 文档文件（支持txt/md/docx/xlsx/pdf）
  - `category`: 文档分类（可选，默认general）

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "accept: application/json" \
  -F "file=@test.docx" \
  -F "category=vehicle_test"
```

**响应**:
```json
{
  "success": true,
  "doc_id": "doc_abc123",
  "filename": "test.docx",
  "category": "vehicle_test",
  "content_length": 5000,
  "message": "Document uploaded successfully"
}
```

#### 1.2 上传文本内容

**接口**: `POST /api/v1/documents/upload-text`

**请求**:
```json
{
  "content": "这是一段测试文本内容...",
  "filename": "test.txt",
  "category": "general",
  "metadata": {
    "source": "external_api",
    "author": "test_user"
  }
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload-text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "测试内容",
    "filename": "test.txt",
    "category": "test"
  }'
```

#### 1.3 删除文档

**接口**: `DELETE /api/v1/documents/{doc_id}`

**示例**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/doc_abc123"
```

#### 1.4 列出文档

**接口**: `GET /api/v1/documents`

**参数**:
- `category`: 按分类过滤（可选）
- `format`: 按格式过滤（可选）

**示例**:
```bash
# 列出所有文档
curl "http://localhost:8000/api/v1/documents"

# 列出特定分类
curl "http://localhost:8000/api/v1/documents?category=vehicle_test"

# 列出特定格式
curl "http://localhost:8000/api/v1/documents?format=.docx"
```

#### 1.5 获取文档详情

**接口**: `GET /api/v1/documents/{doc_id}`

**示例**:
```bash
curl "http://localhost:8000/api/v1/documents/doc_abc123"
```

#### 1.6 获取支持的格式

**接口**: `GET /api/v1/documents/formats`

**示例**:
```bash
curl "http://localhost:8000/api/v1/documents/formats"
```

**响应**:
```json
{
  "supported_formats": {
    "txt": true,
    "md": true,
    "docx": true,
    "xlsx": true,
    "pdf": true
  },
  "description": {
    "txt": "Plain text file",
    "md": "Markdown file",
    "docx": "Microsoft Word document (requires python-docx)",
    "xlsx": "Microsoft Excel spreadsheet (requires openpyxl)",
    "pdf": "PDF document (requires PyPDF2)"
  }
}
```

---

### 2. 查询接口

#### 2.1 基础查询

**接口**: `POST /api/v1/chat`

**请求**:
```json
{
  "query": "蓝牙测试流程是什么？",
  "use_rerank": false,
  "top_k": 5
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "蓝牙测试流程",
    "use_rerank": false,
    "top_k": 5
  }'
```

#### 2.2 外部API查询（标准化）

**接口**: `POST /api/v1/external/query`

**请求**:
```json
{
  "query": "车载测试标准",
  "use_rerank": false,
  "top_k": 5,
  "category": "vehicle_test",
  "return_sources": true
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/external/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "车载测试标准",
    "top_k": 5,
    "return_sources": true
  }'
```

**响应**:
```json
{
  "success": true,
  "query": "车载测试标准",
  "answer": "车载测试标准包括...",
  "sources": [
    {
      "content": "...",
      "score": 0.95,
      "metadata": {...}
    }
  ],
  "metadata": {
    "total_sources": 10,
    "use_rerank": false,
    "engine": "local_tfidf"
  }
}
```

#### 2.3 批量查询

**接口**: `POST /api/v1/external/batch-query`

**请求**:
```json
{
  "queries": [
    "蓝牙测试流程",
    "WiFi测试标准",
    "GPS测试方法"
  ],
  "use_rerank": false,
  "top_k": 5
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/external/batch-query" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["蓝牙测试", "WiFi测试"],
    "top_k": 3
  }'
```

**响应**:
```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "query": "蓝牙测试",
      "answer": "...",
      "sources": [...]
    },
    {
      "success": true,
      "query": "WiFi测试",
      "answer": "...",
      "sources": [...]
    }
  ],
  "total_queries": 2
}
```

---

### 3. 系统管理

#### 3.1 健康检查

**接口**: `GET /health`

**示例**:
```bash
curl "http://localhost:8000/health"
```

#### 3.2 清除缓存

**接口**: `POST /api/v1/system/clear-cache`

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/system/clear-cache"
```

#### 3.3 系统统计

**接口**: `GET /api/v1/system/stats`

**示例**:
```bash
curl "http://localhost:8000/api/v1/system/stats"
```

---

## 🔧 Python调用示例

### 1. 上传文档

```python
import requests

# 上传文件
url = "http://localhost:8000/api/v1/documents/upload"
files = {'file': open('test.docx', 'rb')}
data = {'category': 'vehicle_test'}

response = requests.post(url, files=files, data=data)
print(response.json())

# 上传文本
url = "http://localhost:8000/api/v1/documents/upload-text"
data = {
    "content": "这是一段测试文本",
    "filename": "test.txt",
    "category": "test"
}

response = requests.post(url, json=data)
print(response.json())
```

### 2. 查询

```python
import requests

# 基础查询
url = "http://localhost:8000/api/v1/chat"
data = {
    "query": "蓝牙测试流程",
    "use_rerank": False,
    "top_k": 5
}

response = requests.post(url, json=data)
result = response.json()
print(result["answer"])

# 外部API查询
url = "http://localhost:8000/api/v1/external/query"
data = {
    "query": "车载测试标准",
    "top_k": 5,
    "return_sources": True
}

response = requests.post(url, json=data)
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

### 3. 批量查询

```python
import requests

url = "http://localhost:8000/api/v1/external/batch-query"
data = {
    "queries": [
        "蓝牙测试流程",
        "WiFi测试标准",
        "GPS测试方法"
    ],
    "top_k": 3
}

response = requests.post(url, json=data)
results = response.json()

for result in results["results"]:
    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer'][:100]}...")
    print()
```

---

## 📦 依赖安装

### 基础依赖
```bash
pip install fastapi uvicorn python-multipart
```

### 文档格式支持
```bash
# Word文档
pip install python-docx

# Excel文档
pip install openpyxl

# PDF文档
pip install PyPDF2

# 一次性安装所有
pip install python-docx openpyxl PyPDF2
```

---

## 🎯 使用场景

### 场景1: 外部系统集成
外部系统通过API上传文档并查询：
```python
# 1. 上传文档
upload_result = requests.post(
    "http://localhost:8000/api/v1/documents/upload-text",
    json={
        "content": document_content,
        "filename": "test.txt",
        "category": "external"
    }
)

# 2. 查询
query_result = requests.post(
    "http://localhost:8000/api/v1/external/query",
    json={
        "query": "查询问题",
        "top_k": 5
    }
)
```

### 场景2: 批量处理
批量上传和查询：
```python
# 批量上传
for doc in documents:
    requests.post(
        "http://localhost:8000/api/v1/documents/upload-text",
        json={
            "content": doc["content"],
            "filename": doc["filename"],
            "category": doc["category"]
        }
    )

# 批量查询
queries = ["问题1", "问题2", "问题3"]
result = requests.post(
    "http://localhost:8000/api/v1/external/batch-query",
    json={"queries": queries, "top_k": 5}
)
```

---

## 🚀 性能优化建议

1. **使用缓存**: 避免重复查询
2. **批量操作**: 使用批量查询接口
3. **文档分类**: 合理分类便于检索
4. **定期清理**: 删除无用文档

---

## 📝 注意事项

1. **文件大小**: 建议单个文档不超过10MB
2. **并发限制**: 建议并发不超过10个请求
3. **文档格式**: 确保文档格式正确，编码为UTF-8
4. **元数据**: 合理使用元数据便于管理

---

**API状态**: ✅ 已增强  
**版本**: v1.0-enhanced  
**最后更新**: 2026-03-05
