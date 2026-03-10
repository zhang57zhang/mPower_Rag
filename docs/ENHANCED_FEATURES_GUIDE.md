# mPower_Rag 功能增强指南

**版本**: v1.1.0
**更新时间**: 2026-03-10
**状态**: ✅ 新功能已实现

---

## 🎯 功能概览

### 新增核心功能

1. **多格式文件导入** - 支持 15+ 种文件格式
2. **知识冲突检测** - 自动检测和解决知识矛盾
3. **专家反馈系统** - 支持专家评分、修正和审核

---

## 📦 功能 1: 多格式文件导入

### 支持的文件格式

#### 文档格式
- ✅ **文本文件**: TXT, MD, RTF
- ✅ **Office 文档**: DOCX, XLSX, PPTX
- ✅ **PDF 文档**: PDF（支持扫描件 OCR）
- ✅ **数据文件**: CSV, JSON, XML
- ✅ **图片文件**: JPG, PNG（OCR 提取）
- ✅ **代码文件**: PY, JS, JAVA, C++, C
- ✅ **压缩文件**: ZIP（自动解压）

### 使用方法

#### 1. 单文件上传

```bash
curl -X POST http://localhost:8000/api/v1/documents/import \
  -H "X-API-Key: your_api_key" \
  -F "files=@document.pdf" \
  -F "files=@data.xlsx"
```

#### 2. 目录批量导入

```bash
curl -X POST http://localhost:8000/api/v1/documents/import \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/path/to/documents",
    "incremental": true,
    "auto_detect_conflicts": true
  }'
```

#### 3. Python 代码示例

```python
from src.data.enhanced_loader import get_enhanced_loader

# 初始化加载器
loader = get_enhanced_loader()

# 加载单个文件
content, metadata = loader.load_file("document.pdf")
print(f"格式: {metadata['format']}")
print(f"页数: {metadata.get('page_count', 'N/A')}")

# 批量加载目录
results = loader.load_directory("./documents", recursive=True)
for content, metadata in results:
    print(f"已加载: {metadata['file_path']}")
```

### 特殊功能

#### OCR 图片识别

```python
# 自动识别图片中的文字
content, metadata = loader.load_file("scan.jpg")
print(content)  # OCR 提取的文本
```

#### 智能格式识别

```python
# 自动检测文件类型（即使扩展名错误）
content, metadata = loader.load_file("data.xyz", auto_detect=True)
```

#### 增量更新

```python
# 只处理新增或修改的文件
results = loader.load_directory("./docs", incremental=True)
```

---

## 🔍 功能 2: 知识冲突检测

### 冲突类型

#### 1. 事实冲突 (Factual)
- 同一问题有不同答案
- 示例：文档A说"蓝牙测试需要3步"，文档B说"蓝牙测试需要5步"

#### 2. 逻辑冲突 (Logical)
- 知识之间存在逻辑矛盾
- 示例：文档A说"启用XX功能"，文档B说"禁用XX功能"

#### 3. 时效冲突 (Temporal)
- 新旧知识的时效性冲突
- 示例：2024年的文档与2026年的文档描述不一致

#### 4. 权威冲突 (Authority)
- 不同权威来源的冲突
- 示例：国家标准与企业标准的差异

#### 5. 语义冲突 (Semantic)
- 语义层面的矛盾
- 示例：肯定表述 vs 否定表述

### 使用方法

#### 1. API 调用

```bash
# 检测所有冲突
curl -X POST http://localhost:8000/api/v1/knowledge/check-conflicts \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{}'

# 检测特定类型的冲突
curl -X POST http://localhost:8000/api/v1/knowledge/check-conflicts \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "conflict_types": ["factual", "logical"]
  }'
```

#### 2. Python 代码示例

```python
from src.core.conflict_detector import get_conflict_detector
from src.core.vector_store import get_vector_store
from src.core.embeddings import get_embeddings

# 初始化检测器
vector_store = get_vector_store()
embeddings = get_embeddings()
detector = get_conflict_detector(vector_store, embeddings)

# 检测所有冲突
conflicts = detector.detect_all_conflicts()

for conflict in conflicts:
    print(f"冲突类型: {conflict.conflict_type.value}")
    print(f"严重程度: {conflict.severity.value}")
    print(f"描述: {conflict.description}")
    print(f"建议: {conflict.suggestion}")
    print("---")
```

### 冲突严重程度

- **LOW**: 轻微矛盾，不影响使用
- **MEDIUM**: 明显矛盾，需要注意
- **HIGH**: 严重矛盾，建议尽快处理
- **CRITICAL**: 关键矛盾，必须立即解决

---

## 👨‍🏫 功能 3: 专家反馈系统

### 反馈类型

#### 1. 评分反馈 (Rating)
- 对答案进行 1-5 星评分
- 帮助系统了解答案质量

#### 2. 修正反馈 (Correction)
- 提供正确的答案
- 需要审核后才能实施

#### 3. 批准反馈 (Approval)
- 批准当前答案
- 增加答案的可信度

#### 4. 拒绝反馈 (Rejection)
- 拒绝当前答案
- 标记为不可用

#### 5. 建议反馈 (Suggestion)
- 提供改进建议
- 不直接修改知识库

### 使用流程

#### 1. 提交反馈

```bash
# 提交评分
curl -X POST http://localhost:8000/api/v1/feedback/submit \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "query_123",
    "answer_id": "answer_456",
    "feedback_type": "rating",
    "expert_id": "expert_001",
    "rating": 5,
    "reason": "答案非常准确"
  }'

# 提交修正
curl -X POST http://localhost:8000/api/v1/feedback/submit \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "query_123",
    "answer_id": "answer_456",
    "feedback_type": "correction",
    "expert_id": "expert_001",
    "correction": "正确的答案是...",
    "reason": "原文档描述有误"
  }'
```

#### 2. 审核反馈

```bash
# 审核者审核反馈
curl -X POST http://localhost:8000/api/v1/feedback/feedback_789/review \
  -H "X-API-Key: admin_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer_id": "admin_001",
    "approved": true,
    "comment": "修正准确，批准实施"
  }'
```

#### 3. 实施反馈

```bash
# 实施已批准的修正
curl -X POST http://localhost:8000/api/v1/feedback/feedback_789/implement \
  -H "X-API-Key: admin_api_key"
```

### Python 代码示例

```python
from src.core.expert_feedback import get_expert_feedback_system

# 初始化反馈系统
feedback_system = get_expert_feedback_system()

# 提交反馈
feedback = feedback_system.submit_feedback(
    feedback_type="correction",
    query_id="query_123",
    answer_id="answer_456",
    expert_id="expert_001",
    correction="正确的答案是...",
    reason="原文档描述有误"
)

print(f"反馈已提交: {feedback.id}")
print(f"审核状态: {feedback.review_status.value}")

# 审核反馈
reviewed = feedback_system.review_feedback(
    feedback_id=feedback.id,
    reviewer_id="admin_001",
    approved=True,
    comment="修正准确"
)

# 实施反馈
from src.core.vector_store import get_vector_store
vector_store = get_vector_store()

success = feedback_system.implement_feedback(
    feedback_id=feedback.id,
    vector_store=vector_store
)

if success:
    print("知识库已更新！")
```

### 知识版本管理

#### 查看版本历史

```bash
curl http://localhost:8000/api/v1/knowledge/knowledge_123/versions \
  -H "X-API-Key: your_api_key"
```

#### 回滚到指定版本

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/knowledge_123/rollback/5 \
  -H "X-API-Key: admin_api_key"
```

---

## 📊 完整工作流程示例

### 场景：导入新文档并检测冲突

```python
# 1. 导入文档
from src.data.enhanced_loader import get_enhanced_loader

loader = get_enhanced_loader()
results = loader.load_directory("./new_documents", incremental=True)

print(f"导入了 {len(results)} 个文档")

# 2. 检测冲突
from src.core.conflict_detector import get_conflict_detector
from src.core.vector_store import get_vector_store
from src.core.embeddings import get_embeddings

vector_store = get_vector_store()
embeddings = get_embeddings()
detector = get_conflict_detector(vector_store, embeddings)

conflicts = detector.detect_all_conflicts()

if conflicts:
    print(f"发现 {len(conflicts)} 个冲突:")
    for c in conflicts:
        print(f"- {c.conflict_type.value}: {c.description}")
        print(f"  建议: {c.suggestion}")

# 3. 提交修正
from src.core.expert_feedback import get_expert_feedback_system

feedback_system = get_expert_feedback_system()

for conflict in conflicts:
    if conflict.conflict_type.value == "factual":
        # 提交修正
        feedback = feedback_system.submit_feedback(
            feedback_type="correction",
            query_id="auto_detected",
            answer_id=conflict.documents[0]['id'],
            expert_id="expert_001",
            correction="正确的描述是...",
            reason="解决冲突"
        )
        print(f"已提交修正: {feedback.id}")

# 4. 审核并实施
# （由管理员通过 API 或前端完成）
```

---

## 🎨 前端集成

### Streamlit 界面增强

```python
# frontend/enhanced_app.py
import streamlit as st

# 文件上传界面
st.title("📚 知识库管理")

# 多文件上传
uploaded_files = st.file_uploader(
    "上传文档",
    type=['txt', 'md', 'pdf', 'docx', 'xlsx', 'pptx', 'csv', 'json', 'xml'],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("导入文档"):
        with st.spinner("正在导入..."):
            # 调用 API 导入
            # ...

# 冲突检测界面
st.subheader("🔍 冲突检测")

if st.button("检测冲突"):
    with st.spinner("正在检测..."):
        # 调用 API 检测冲突
        # ...

        st.warning("发现 3 个冲突")
        # 显示冲突列表

# 专家反馈界面
st.subheader("👨‍🏫 专家反馈")

feedback_type = st.selectbox(
    "反馈类型",
    ["评分", "修正", "建议"]
)

if feedback_type == "评分":
    rating = st.slider("评分", 1, 5, 3)
    if st.button("提交评分"):
        # 提交反馈
        # ...

elif feedback_type == "修正":
    correction = st.text_area("修正内容")
    reason = st.text_input("原因")
    if st.button("提交修正"):
        # 提交反馈
        # ...
```

---

## ✅ 新功能清单

### 文件导入
- [x] 支持 15+ 种文件格式
- [x] 自动格式识别
- [x] OCR 图片识别
- [x] 增量导入
- [x] 批量导入

### 冲突检测
- [x] 事实冲突检测
- [x] 逻辑冲突检测
- [x] 时效冲突检测
- [x] 权威冲突检测
- [x] 语义冲突检测
- [x] 自动生成解决建议

### 专家反馈
- [x] 评分反馈
- [x] 修正反馈
- [x] 审核流程
- [x] 知识更新
- [x] 版本管理
- [x] 回滚功能

---

## 📝 更新日志

### v1.1.0 (2026-03-10)

#### 新增
- ✅ 多格式文件导入（15+ 种格式）
- ✅ OCR 图片识别
- ✅ 知识冲突自动检测（5 种类型）
- ✅ 专家反馈系统（5 种类型）
- ✅ 知识版本管理
- ✅ 回滚功能

#### 改进
- 🔄 优化文件解析性能
- 🔄 增强冲突检测算法
- 🔄 完善审核流程

---

## 🚀 下一步计划

### v1.2.0
- [ ] 知识图谱集成
- [ ] 多模态支持（音频、视频）
- [ ] 自动知识抽取
- [ ] 协作编辑功能

### v1.3.0
- [ ] AI 辅助审核
- [ ] 知识质量评分
- [ ] 自动冲突解决
- [ ] 知识推荐系统

---

**功能状态**: ✅ 已实现并测试
**文档版本**: v1.1.0
**最后更新**: 2026-03-10
