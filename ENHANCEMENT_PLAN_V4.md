# mPower_Rag 功能增强计划 V4

**创建时间**: 2026-03-10 13:00
**版本**: 1.1.0
**状态**: 🚀 进行中

---

## 🎯 增强目标

### 1. 多格式文件导入增强
- ✅ 当前支持：TXT, MD, DOCX, XLSX, PDF
- 🆕 新增支持：CSV, JSON, XML, PPTX, 图片（OCR）
- 🆕 智能解析：自动识别文件类型
- 🆕 批量导入：支持整个目录导入
- 🆕 增量更新：只处理新增和修改的文件

### 2. 知识自检与冲突优化
- 🆕 矛盾检测：自动检测知识点之间的矛盾
- 🆕 一致性检查：验证知识的逻辑一致性
- 🆕 冲突标记：标记冲突的知识点
- 🆕 解决建议：提供解决矛盾的建议
- 🆕 自动优化：根据置信度自动选择最优答案

### 3. 专家知识调整系统
- 🆕 知识编辑：支持在线编辑知识点
- 🆕 反馈机制：专家可以对答案进行评分和修正
- 🆕 权重调整：根据专家反馈调整知识权重
- 🆕 版本管理：记录知识的变更历史
- 🆕 审核流程：知识更新需要专家审核

---

## 📋 详细功能设计

### 模块 1: 多格式文件导入器

#### 支持格式
```
文档类型：
- 文本文件：TXT, MD, RTF
- Office 文档：DOCX, XLSX, PPTX
- 数据文件：CSV, JSON, XML
- PDF 文档：PDF（支持扫描件 OCR）
- 图片文件：JPG, PNG（OCR 提取）
- 代码文件：PY, JS, JAVA 等

压缩文件：
- ZIP, TAR, GZ（自动解压并导入）
```

#### 功能特性
- 自动格式识别
- 智能内容提取
- 表格结构保留
- 图片 OCR 识别
- 代码语法高亮

---

### 模块 2: 知识冲突检测器

#### 检测类型
1. **事实冲突**：同一问题有不同答案
2. **逻辑冲突**：知识之间存在逻辑矛盾
3. **时效冲突**：新旧知识的时效性冲突
4. **权威冲突**：不同来源的权威性差异

#### 处理策略
- 自动标记冲突
- 计算置信度
- 提供解决建议
- 支持人工审核

---

### 模块 3: 专家知识管理系统

#### 功能模块
1. **知识编辑器**
   - 在线编辑知识点
   - 富文本支持
   - 预览和保存

2. **反馈系统**
   - 答案评分（1-5星）
   - 错误报告
   - 改进建议

3. **权重管理**
   - 知识权重调整
   - 来源可信度
   - 时效性评分

4. **版本控制**
   - 变更历史
   - 回滚功能
   - 差异对比

5. **审核流程**
   - 提交审核
   - 专家评审
   - 批准/拒绝

---

## 🏗️ 技术架构

### 新增模块

```
src/
├── core/
│   ├── knowledge_validator.py     # 知识验证器
│   ├── conflict_detector.py       # 冲突检测器
│   └── expert_feedback.py         # 专家反馈系统
│
├── data/
│   ├── enhanced_loader.py         # 增强文件加载器
│   ├── format_parser/             # 格式解析器
│   │   ├── csv_parser.py
│   │   ├── json_parser.py
│   │   ├── xml_parser.py
│   │   ├── pptx_parser.py
│   │   └── ocr_parser.py
│   └── incremental_updater.py     # 增量更新器
│
├── api/
│   ├── knowledge_management.py    # 知识管理 API
│   └── expert_interface.py        # 专家接口
│
└── models/
    ├── knowledge.py               # 知识模型
    ├── feedback.py                # 反馈模型
    └── conflict.py                # 冲突模型
```

---

## 📊 API 接口设计

### 1. 文件导入 API

```http
POST /api/v1/documents/import
Content-Type: multipart/form-data

# 参数
- file: 文件（支持多文件）
- directory: 目录路径（可选）
- incremental: 是否增量导入（默认 false）
- auto_detect_conflicts: 是否自动检测冲突（默认 true）

# 响应
{
  "imported": 10,
  "skipped": 2,
  "conflicts": [
    {
      "id": "conflict_1",
      "documents": ["doc1.txt", "doc2.txt"],
      "type": "factual",
      "description": "关于蓝牙测试流程的描述存在冲突"
    }
  ]
}
```

### 2. 知识冲突检测 API

```http
POST /api/v1/knowledge/check-conflicts

# 响应
{
  "total_documents": 100,
  "conflicts_found": 5,
  "conflicts": [
    {
      "id": "conflict_1",
      "type": "factual",
      "severity": "high",
      "documents": [
        {
          "id": "doc1",
          "content": "蓝牙测试需要3步...",
          "confidence": 0.85
        },
        {
          "id": "doc2",
          "content": "蓝牙测试需要5步...",
          "confidence": 0.75
        }
      ],
      "suggestion": "建议采用 doc1 的描述，置信度更高"
    }
  ]
}
```

### 3. 专家反馈 API

```http
POST /api/v1/feedback/submit
Content-Type: application/json

{
  "query_id": "query_123",
  "answer_id": "answer_456",
  "rating": 5,
  "feedback_type": "correction",
  "correct_answer": "正确的答案是...",
  "reason": "原文档描述有误",
  "expert_id": "expert_001"
}

# 响应
{
  "status": "submitted",
  "feedback_id": "feedback_789",
  "review_status": "pending"
}
```

### 4. 知识编辑 API

```http
PUT /api/v1/knowledge/{knowledge_id}
Content-Type: application/json

{
  "content": "更新后的知识内容",
  "metadata": {
    "source": "专家修正",
    "confidence": 0.95,
    "reviewed_by": "expert_001"
  }
}
```

---

## 🔄 工作流程

### 文件导入流程
```
1. 上传文件
   ↓
2. 自动识别格式
   ↓
3. 解析内容
   ↓
4. 提取文本和元数据
   ↓
5. 向量化存储
   ↓
6. 冲突检测
   ↓
7. 返回结果
```

### 冲突检测流程
```
1. 扫描知识库
   ↓
2. 提取关键信息
   ↓
3. 语义相似度计算
   ↓
4. 识别矛盾点
   ↓
5. 计算置信度
   ↓
6. 生成解决建议
   ↓
7. 提交审核（可选）
```

### 专家反馈流程
```
1. 用户提交反馈
   ↓
2. 系统记录反馈
   ↓
3. 专家审核
   ↓
4. 批准/拒绝
   ↓
5. 更新知识库
   ↓
6. 重新索引
```

---

## ✅ 完成标准

### 功能完整性
- [ ] 支持 10+ 种文件格式
- [ ] 冲突检测准确率 > 80%
- [ ] 专家反馈系统完整
- [ ] 知识编辑功能可用
- [ ] 版本管理完善

### 性能要求
- [ ] 文件导入速度 > 1MB/s
- [ ] 冲突检测 < 30s（1000个文档）
- [ ] 反馈提交响应 < 1s
- [ ] 知识更新 < 5s

### 用户体验
- [ ] 操作简单直观
- [ ] 错误提示清晰
- [ ] 文档详细完整
- [ ] 示例丰富

---

## 📅 实施计划

### 第 1 周：文件导入增强
- Day 1-2: CSV, JSON, XML 解析器
- Day 3-4: PPTX 解析器
- Day 5: OCR 集成
- Day 6-7: 测试和优化

### 第 2 周：冲突检测系统
- Day 1-2: 冲突检测算法
- Day 3-4: 置信度计算
- Day 5-6: 解决建议生成
- Day 7: 测试和优化

### 第 3 周：专家反馈系统
- Day 1-3: 反馈系统开发
- Day 4-5: 知识编辑功能
- Day 6-7: 版本管理

### 第 4 周：集成测试
- Day 1-3: 功能集成
- Day 4-5: 性能测试
- Day 6-7: 文档完善

---

## 📝 备注

- 优先完成核心功能
- 保持代码质量
- 完善测试覆盖
- 及时更新文档

---

**最后更新**: 2026-03-10 13:00
