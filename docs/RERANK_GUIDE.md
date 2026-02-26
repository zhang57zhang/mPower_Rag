# 重排序功能说明

**版本**: 1.0
**最后更新**: 2026-02-23

---

## 📋 功能概述

重排序（Rerank）是 RAG 系统中的重要优化技术，通过在初始检索结果基础上进行二次排序，提高检索的准确性和相关性。

### 核心特性

- ✅ **交叉编码器重排序** - 使用预训练的交叉编码器模型
- ✅ **可配置开关** - 根据需求启用或禁用重排序
- ✅ **性能优化** - 只检索更多文档供重排序
- ✅ **无缝集成** - 集成到现有 RAG 流程中

---

## 🎯 为什么需要重排序？

### 传统检索的局限性

1. **语义相似度不等于相关性**
   - 向量相似度高不一定代表最相关
   - 可能遗漏真正相关但表达方式不同的文档

2. **检索范围受限**
   - 传统检索通常只返回 Top K 个结果
   - 可能遗漏稍低于阈值的高质量文档

### 重排序的优势

1. **更准确的排序**
   - 基于问题和文档的联合表示计算相关性
   - 可以捕获更细粒度的语义关系

2. **更全面的结果**
   - 先检索更多候选文档（2x）
   - 再通过重排序选出最好的 K 个

3. **灵活的调整**
   - 可以根据需求选择是否启用
   - 可以调整重排序模型和方法

---

## 🏗️ 架构设计

### 流程图

```
用户提问
    ↓
向量检索（检索 2x 文档）
    ↓
候选文档列表
    ↓
重排序（交叉编码器）
    ↓
重新排序后的文档
    ↓
Top K 个文档
    ↓
生成答案
```

### 代码流程

```python
# 1. 初始检索（检索 2x 文档）
retrieval_k = top_k * 2  # 例如：5 * 2 = 10
docs_with_scores = vector_store.similarity_search_with_score(
    query=question, k=retrieval_k
)

# 2. 重排序
if use_rerank and reranker:
    reranked_docs = reranker.rerank(
        query=query,
        documents=[doc.page_content for doc in documents]
    )

# 3. 返回 Top K
reranked_docs = reranked_docs[:top_k]
```

---

## ⚙️ 配置选项

### 环境变量

```env
# 重排序配置
RERANK_ENABLED=false          # 是否启用重排序
RERANK_METHOD=cross_encoder  # 重排序方法
RERANK_MODEL=BAAI/bge-reranker-base  # 重排序模型
```

### API 请求参数

```json
{
  "question": "用户问题",
  "top_k": 5,
  "use_rerank": true  // 是否使用重排序
}
```

### 重排序方法

| 方法 | 说明 | 模型 |
|------|------|------|
| `cross_encoder` | 交叉编码器重排序 | `BAAI/bge-reranker-base` |
| `keyword` | 关键词重排序 | （待实现）|

### 推荐模型

| 模型 | 语言 | 大小 | 速度 | 精度 |
|------|------|------|------|------|
| `BAAI/bge-reranker-base` | 中英文 | 400MB | 快 | 高 |
| `BAAI/bge-reranker-large` | 中英文 | 1.3GB | 中 | 很高 |
| `BAAI/bge-reranker-v2-m3` | 多语言 | 2.2GB | 慢 | 很高 |

---

## 🎨 使用示例

### 1. 启用重排序

#### 方法 1：环境变量

```env
RERANK_ENABLED=true
RERANK_METHOD=cross_encoder
RERANK_MODEL=BAAI/bge-reranker-base
```

#### 方法 2：API 请求

```json
{
  "question": "什么是车载测试？",
  "top_k": 5,
  "use_rerank": true
}
```

### 2. 对比测试

```python
# 不使用重排序
result_without = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"question": "什么是车载测试？", "use_rerank": False}
)

# 使用重排序
result_with = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"question": "什么是车载测试？", "use_rerank": True}
)

# 对比结果
print("不使用重排序:", result_without.json()['answer'][:100])
print("使用重排序:", result_with.json()['answer'][:100])
```

### 3. 前端配置

在 Streamlit 前端中：
- 侧边栏配置区域添加"启用重排序"复选框
- 勾选后所有查询都会使用重排序

---

## 📊 性能分析

### 预期性能

| 指标 | 不使用重排序 | 使用重排序 | 开销 |
|------|------------|-----------|-----|
| 检索时间 | ~0.1s | ~0.1s | 0 |
| 重排序时间 | 0s | ~0.3-0.5s | +300-500ms |
| 总响应时间 | ~2-3s | ~2.5-3.5s | +10-20% |
| 检索准确率 | 85% | 92% | +7% |

### 优化建议

1. **选择合适的模型**
   - 基础模型（base）：速度快，适合生产
   - 大型模型（large）：精度高，适合离线分析

2. **调整检索数量**
   - 检索更多候选文档（2x 或 3x）
   - 平衡性能和精度

3. **缓存重排序结果**
   - 对相似问题缓存结果
   - 减少重复计算

---

## 🔧 实现细节

### 1. 重排序器集成

```python
from .rerank import CrossEncoderReranker

class RAGEngine:
    def __init__(self, ..., use_rerank=False, ...):
        self.use_rerank = use_rerank
        self.reranker = None

        if self.use_rerank:
            self.reranker = CrossEncoderReranker(
                model_name="BAAI/bge-reranker-base"
            )
```

### 2. 检索流程

```python
def query_with_sources(self, question: str, top_k: int = 5):
    # 检索更多候选文档
    retrieval_k = top_k * 2 if self.use_rerank else top_k
    docs = self.vector_store.similarity_search_with_score(
        query=question, k=retrieval_k
    )

    # 重排序
    if self.use_rerank and self.reranker:
        docs = self._rerank_documents(docs, question, top_k)

    return docs[:top_k]
```

### 3. 重排序方法

```python
def _rerank_documents(self, documents, query, top_k):
    texts = [doc.page_content for doc in documents]
    scores = self.reranker.rerank(query=query, documents=texts)

    # 重新排序
    reranked = [
        (documents[i], scores[i])
        for i in range(len(documents))
    ]
    reranked.sort(key=lambda x: x[1], reverse=True)

    return reranked[:top_k]
```

---

## 🧪 测试

### 测试脚本

```bash
# 运行重排序测试
python scripts/test_rerank.py
```

### 测试覆盖

1. **功能测试**
   - ✅ 不使用重排序的问答
   - ✅ 使用重排序的问答
   - ✅ 带重排序的多轮对话

2. **性能测试**
   - ✅ 响应时间对比
   - ✅ 性能开销测量

3. **准确性测试**
   - ✅ 检索结果对比
   - ✅ 相关性评估

---

## ⚠️ 注意事项

### 1. 依赖安装

重排序功能需要 `sentence-transformers` 包：

```bash
pip install sentence-transformers
```

**注意**：需要 Python 3.10-3.11

### 2. 模型下载

首次使用时，重排序模型会自动下载：
- 模型大小：~400MB（base）
- 下载时间：取决于网络速度
- 下载位置：`~/.cache/huggingface/`

### 3. 资源消耗

- **内存**：模型加载后占用 ~500MB 内存
- **GPU**：建议使用 GPU 加速（可选）
- **CPU**：重排序会增加 CPU 使用率

### 4. 响应时间

- 首次查询较慢（需要加载模型）
- 后续查询正常
- 建议预热模型

---

## 🔮 未来改进

### 短期

1. **支持更多重排序方法**
   - 关键词重排序
   - 混合重排序

2. **优化性能**
   - 模型缓存
   - 批量重排序
   - GPU 加速

3. **更好的集成**
   - 自适应重排序
   - 基于查询复杂度调整

### 长期

4. **多语言支持**
   - 针对不同语言优化
   - 领域专用模型

5. **学习型重排序**
   - 基于用户反馈学习
   - 自适应调整权重

---

## 📚 参考资料

### 论文
- [BGE Reranker](https://arxiv.org/abs/2309.07597)
- [ColBERT](https://arxiv.org/abs/2004.12853)
- [MonoT5](https://arxiv.org/abs/2107.06117)

### 代码
- [sentence-transformers](https://www.sbert.net/)
- [FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding)

### 模型
- [Hugging Face Models](https://huggingface.co/models?search=rerank)

---

## 🆘 常见问题

### Q: 重排序一定会提高准确性吗？
A: 不一定。取决于查询类型和数据质量。建议进行 A/B 测试。

### Q: 重排序会增加多少延迟？
A: 通常增加 300-500ms，具体取决于模型和硬件。

### Q: 可以使用自定义重排序模型吗？
A: 可以。修改配置文件中的 `RERANK_MODEL` 参数。

### Q: 重排序会消耗多少内存？
A: 模型加载后占用 ~500MB 内存（base 模型）。

### Q: 什么时候应该启用重排序？
A: 当检索质量不如预期，或对准确性要求较高时。

---

**最后更新**: 2026-02-23
**版本**: 1.0
**维护者**: AI 助手
