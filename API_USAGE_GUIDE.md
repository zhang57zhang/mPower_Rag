# mPower_Rag API 使用指南

## 📋 目录
1. [快速开始](#快速开始)
2. [文档管理](#文档管理)
3. [智能问答](#智能问答)
4. [外部API集成](#外部api集成)
5. [Phase 2新功能](#phase-2新功能)
6. [示例代码](#示例代码)

---

## 快速开始

### 启动服务
```bash
cd E:\workspace\mPower_Rag
python simple_api.py
```

### 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 健康检查
```bash
curl http://localhost:8000/health
```

---

## 文档管理

### 1. 上传文档（支持多格式）

**支持的格式:** `.txt`, `.md`, `.docx`, `.xlsx`, `.pdf`

```bash
# 上传TXT文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@test.txt"

# 上传Word文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@report.docx"

# 上传PDF文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@manual.pdf"
```

**响应示例:**
```json
{
  "message": "Document uploaded successfully",
  "filename": "test.txt",
  "format": "txt",
  "size": 1024,
  "document_count": 3
}
```

### 2. 列出所有文档

```bash
curl -X GET "http://localhost:8000/api/v1/documents/list"
```

### 3. 删除文档

```bash
# 删除单个文档
curl -X DELETE "http://localhost:8000/api/v1/documents/{doc_id}"

# 批量删除
curl -X POST "http://localhost:8000/api/v1/documents/batch-delete" \
  -H "Content-Type: application/json" \
  -d '{"doc_ids": ["id1", "id2"]}'
```

---

## Phase 2新功能

### 1. 批量上传文档 ✨

**接口:** `POST /api/v1/documents/batch-upload`

**功能:** 一次上传多个文档，支持所有格式

**示例:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/batch-upload" \
  -F "files=@doc1.txt" \
  -F "files=@doc2.pdf" \
  -F "files=@doc3.docx"
```

**Python示例:**
```python
import requests

files = [
    ('files', ('doc1.txt', open('doc1.txt', 'rb'), 'text/plain')),
    ('files', ('doc2.pdf', open('doc2.pdf', 'rb'), 'application/pdf'))
]

response = requests.post(
    "http://localhost:8000/api/v1/documents/batch-upload",
    files=files
)

result = response.json()
print(f"成功: {result['success_count']}, 失败: {result['failed_count']}")
```

**响应示例:**
```json
{
  "message": "批量上传完成: 2 成功, 0 失败",
  "success_count": 2,
  "failed_count": 0,
  "total_documents": 5,
  "results": [
    {
      "filename": "doc1.txt",
      "success": true,
      "format": "txt",
      "size": 1024
    },
    {
      "filename": "doc2.pdf",
      "success": true,
      "format": "pdf",
      "size": 2048
    }
  ]
}
```

### 2. 导入整个目录 ✨

**接口:** `POST /api/v1/documents/import-directory`

**功能:** 导入指定目录的所有文档，支持递归扫描

**示例:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/import-directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "E:/documents",
    "recursive": true,
    "file_extensions": [".txt", ".pdf", ".docx"]
  }'
```

**Python示例:**
```python
import requests

data = {
    "directory_path": "E:/documents",
    "recursive": True,  # 递归扫描子目录
    "file_extensions": [".txt", ".pdf", ".docx"]  # 只导入这些格式
}

response = requests.post(
    "http://localhost:8000/api/v1/documents/import-directory",
    json=data
)

result = response.json()
print(f"找到文件: {result['files_found']}")
print(f"导入成功: {result['imported_count']}")
```

**响应示例:**
```json
{
  "message": "目录导入完成: 15 成功, 0 失败",
  "directory": "E:/documents",
  "recursive": true,
  "scanned_extensions": [".txt", ".pdf", ".docx"],
  "files_found": 15,
  "imported_count": 15,
  "failed_count": 0,
  "total_documents": 20,
  "results": [
    {
      "filename": "report.txt",
      "path": "E:/documents/report.txt",
      "success": true,
      "format": "txt",
      "size": 2048
    }
  ]
}
```

### 3. 文档大小限制 📏

**限制:** 单个文件最大 **10MB**

**超过限制时的响应:**
```json
{
  "filename": "large_file.pdf",
  "success": false,
  "error": "文件过大，最大支持10MB"
}
```

---

## 智能问答

### 基本查询

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "车载蓝牙测试标准",
    "top_k": 5
  }'
```

**响应示例:**
```json
{
  "answer": "根据知识库信息，车载蓝牙测试包括...",
  "sources": [
    {
      "content": "蓝牙测试标准...",
      "metadata": {
        "filename": "bluetooth_test_guide.txt",
        "format": "txt"
      },
      "score": 0.95
    }
  ],
  "query": "车载蓝牙测试标准",
  "llm_used": true
}
```

---

## 外部API集成

### 从外部API导入

```bash
curl -X POST "http://localhost:8000/api/v1/documents/import-from-api" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.example.com/docs/123",
    "headers": {
      "Authorization": "Bearer token"
    }
  }'
```

---

## 示例代码

### Python 完整示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 批量上传
def batch_upload():
    files = [
        ('files', ('doc1.txt', open('doc1.txt', 'rb'), 'text/plain')),
        ('files', ('doc2.pdf', open('doc2.pdf', 'rb'), 'application/pdf'))
    ]
    response = requests.post(f"{BASE_URL}/documents/batch-upload", files=files)
    return response.json()

# 2. 导入目录
def import_directory():
    data = {
        "directory_path": "E:/documents",
        "recursive": True,
        "file_extensions": [".txt", ".pdf"]
    }
    response = requests.post(f"{BASE_URL}/documents/import-directory", json=data)
    return response.json()

# 3. 查询
def query(question):
    data = {"query": question, "top_k": 5}
    response = requests.post(f"{BASE_URL}/chat", json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 批量上传
    result = batch_upload()
    print(f"上传成功: {result['success_count']}")

    # 导入目录
    result = import_directory()
    print(f"导入成功: {result['imported_count']}")

    # 查询
    answer = query("如何测试蓝牙连接？")
    print(f"回答: {answer['answer']}")
```

---

## 常见问题

### Q1: 批量上传支持多少个文件？
**A:** 没有硬性限制，但建议单次不超过100个文件，以确保稳定性。

### Q2: 导入目录时会递归扫描子目录吗？
**A:** 可选。设置 `"recursive": true` 会递归扫描所有子目录。

### Q3: 如何只导入特定格式的文件？
**A:** 使用 `file_extensions` 参数过滤，例如：`["file_extensions": [".txt", ".pdf"]]`

### Q4: 文件大小超限怎么办？
**A:** 单个文件最大10MB，超过限制的文件会被跳过并在结果中标注错误。

### Q5: 批量操作失败会影响其他文件吗？
**A:** 不会。每个文件独立处理，一个失败不影响其他文件。

---

## 更新日志

### v1.2.0 (2026-03-05 - Phase 2)
- ✨ 新增批量上传接口
- ✨ 新增目录导入功能
- ✨ 新增文档大小限制检查
- ✨ 性能优化（批量操作）
- ✨ 完善错误处理

### v1.1.0 (2026-03-05 - Phase 1)
- ✅ 新增多格式文档支持（DOCX/XLSX/PDF/MD）
- ✅ 新增文档删除功能（单个/批量）
- ✅ 新增外部API集成
- ✅ 新增文档列表查询

### v1.0.0 (2026-02-26)
- ✅ 基础RAG问答功能
- ✅ TXT文档上传
- ✅ 向量检索
- ✅ LLM集成

---

*文档版本: v1.2.0*
*最后更新: 2026-03-05*

---

## 快速开始

### 启动服务
```bash
cd E:\workspace\mPower_Rag
python simple_api.py
```

### 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 健康检查
```bash
curl http://localhost:8000/health
```

---

## 文档管理

### 1. 上传文档（支持多格式）

**支持的格式:** `.txt`, `.md`, `.docx`, `.xlsx`, `.pdf`

```bash
# 上传TXT文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@test.txt"

# 上传Word文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@report.docx"

# 上传PDF文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@manual.pdf"

# 上传Excel文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@data.xlsx"

# 上传Markdown文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@readme.md"
```

**响应示例:**
```json
{
  "message": "Document uploaded successfully",
  "filename": "test.txt",
  "format": "txt",
  "size": 1024,
  "document_count": 3
}
```

### 2. 列出所有文档

```bash
curl -X GET "http://localhost:8000/api/v1/documents/list"
```

**响应示例:**
```json
{
  "total": 3,
  "documents": [
    {
      "id": "test_txt_97aadbba",
      "metadata": {
        "filename": "test.txt",
        "format": "txt",
        "size": 1024
      },
      "content_preview": "This is the first 100 characters..."
    }
  ]
}
```

### 3. 删除单个文档

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/test_txt_97aadbba"
```

**响应示例:**
```json
{
  "message": "Document deleted successfully",
  "doc_id": "test_txt_97aadbba",
  "remaining_documents": 2
}
```

### 4. 批量删除文档

```bash
curl -X POST "http://localhost:8000/api/v1/documents/batch-delete" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_ids": [
      "test1_txt_97aadbba",
      "test2_txt_fc67bd5a"
    ]
  }'
```

**响应示例:**
```json
{
  "message": "Batch delete completed: 2 success, 0 failed",
  "results": {
    "test1_txt_97aadbba": true,
    "test2_txt_fc67bd5a": true
  },
  "success_count": 2,
  "failed_count": 0,
  "remaining_documents": 1
}
```

### 5. 获取文档统计信息

```bash
curl -X GET "http://localhost:8000/api/v1/documents/stats"
```

### 6. 获取支持的格式

```bash
curl -X GET "http://localhost:8000/api/v1/formats"
```

---

## 智能问答

### 1. 基本查询

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "车载蓝牙模块的连接稳定性测试方法",
    "top_k": 5
  }'
```

**响应示例:**
```json
{
  "answer": "根据知识库中的信息，车载蓝牙模块的连接稳定性测试包括...",
  "sources": [
    {
      "content": "蓝牙连接测试标准...",
      "metadata": {
        "filename": "bluetooth_test_guide.txt",
        "format": "txt"
      },
      "score": 0.95
    }
  ],
  "query": "车载蓝牙模块的连接稳定性测试方法",
  "llm_used": true
}
```

### 2. 外部系统查询

```bash
curl -X POST "http://localhost:8000/api/v1/query-from-external" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ECU故障诊断流程",
    "top_k": 3,
    "use_rerank": false
  }'
```

**响应示例:**
```json
{
  "answer": "ECU故障诊断流程包括以下步骤...",
  "sources": [...],
  "api_version": "1.0.0",
  "query_timestamp": 1709607600.123
}
```

---

## 外部API集成

### 1. 从外部API导入文档

```bash
curl -X POST "http://localhost:8000/api/v1/documents/import-from-api" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.example.com/documents/123",
    "headers": {
      "Authorization": "Bearer your_token_here"
    },
    "params": {
      "format": "json"
    },
    "metadata": {
      "category": "test_guide",
      "version": "2.0"
    }
  }'
```

**外部API响应格式（推荐）:**
```json
{
  "content": "文档内容...",
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "date": "2026-03-05"
  }
}
```

**如果外部API返回纯文本:**
- 系统会自动将整个响应作为文档内容
- 元数据中会标记为`"format": "text"`

**响应示例:**
```json
{
  "message": "Document imported successfully from external API",
  "source_url": "https://api.example.com/documents/123",
  "content_length": 2048,
  "document_count": 4
}
```

### 2. 外部API认证方式

#### Bearer Token
```json
{
  "headers": {
    "Authorization": "Bearer your_token_here"
  }
}
```

#### API Key
```json
{
  "headers": {
    "X-API-Key": "your_api_key_here"
  }
}
```

#### Basic Auth
```python
# 使用Python生成Basic Auth头
import base64
credentials = base64.b64encode(b"username:password").decode()
headers = {"Authorization": f"Basic {credentials}"}
```

---

## 示例代码

### Python 示例

```python
import requests

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 1. 上传文档
def upload_document(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/documents/upload", files=files)
    return response.json()

# 2. 列出文档
def list_documents():
    response = requests.get(f"{BASE_URL}/documents/list")
    return response.json()

# 3. 查询
def query_knowledge_base(question):
    data = {
        "query": question,
        "top_k": 5
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    return response.json()

# 4. 删除文档
def delete_document(doc_id):
    response = requests.delete(f"{BASE_URL}/documents/{doc_id}")
    return response.json()

# 5. 从外部API导入
def import_from_api(url, token):
    data = {
        "url": url,
        "headers": {"Authorization": f"Bearer {token}"}
    }
    response = requests.post(f"{BASE_URL}/documents/import-from-api", json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 上传文档
    result = upload_document("test.txt")
    print("上传结果:", result)

    # 查询
    answer = query_knowledge_base("如何测试蓝牙连接？")
    print("查询结果:", answer['answer'])
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 1. 上传文档
async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData
  });

  return await response.json();
}

// 2. 查询
async function queryKnowledgeBase(question) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      query: question,
      top_k: 5
    })
  });

  return await response.json();
}

// 3. 从外部API导入
async function importFromApi(url, token) {
  const response = await fetch(`${BASE_URL}/documents/import-from-api`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      url: url,
      headers: {Authorization: `Bearer ${token}`}
    })
  });

  return await response.json();
}
```

---

## 常见问题

### Q1: 支持哪些文档格式？
**A:** 支持 `.txt`, `.md`, `.docx`, `.xlsx`, `.pdf` 五种格式。

### Q2: 文档大小有限制吗？
**A:** 目前没有硬性限制，但建议单个文档不超过10MB。

### Q3: 如何获取文档ID？
**A:** 使用 `GET /api/v1/documents/list` 接口列出所有文档及其ID。

### Q4: 外部API返回什么格式？
**A:** 推荐返回JSON格式 `{"content": "...", "metadata": {...}}`，也支持纯文本。

### Q5: 删除文档后能恢复吗？
**A:** 不能，删除操作是永久性的，建议先备份重要文档。

### Q6: 如何处理中文文档？
**A:** 系统自动支持UTF-8和GBK编码，无需额外配置。

---

## 性能建议

1. **批量操作**: 使用批量删除接口，减少网络请求次数
2. **文档大小**: 单个文档建议不超过10MB，过大的文档应拆分
3. **查询优化**: 合理设置`top_k`参数，避免返回过多结果
4. **缓存利用**: 系统内置缓存机制，重复查询会更快

---

## 更新日志

### v1.1.0 (2026-03-05)
- ✅ 新增多格式文档支持（DOCX/XLSX/PDF/MD）
- ✅ 新增文档删除功能（单个/批量）
- ✅ 新增外部API集成
- ✅ 新增文档列表查询
- ✅ 优化启动加载器

### v1.0.0 (2026-02-26)
- ✅ 基础RAG问答功能
- ✅ TXT文档上传
- ✅ 向量检索
- ✅ LLM集成

---

*文档版本: v1.1.0*
*最后更新: 2026-03-05*
