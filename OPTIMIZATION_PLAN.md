# mPower_Rag 优化计划

## 📋 优化目标

### 用户需求（2026-03-05 00:30）
1. ✅ **支持删除车载知识库文档**
2. ✅ **多格式文档支持**（Word/Excel/PDF/MD/TXT）
3. ✅ **外部API调用**（从外部API获取知识库文档与查询知识）

---

## 🎯 Phase 1: 核心功能（2-3小时）

### 1.1 文档删除功能 ⏱️ 30分钟
**新增接口：**
- `DELETE /api/v1/documents/{doc_id}` - 删除单个文档
- `DELETE /api/v1/documents/batch` - 批量删除文档
- `GET /api/v1/documents/list` - 列出所有文档（带ID）

**实现要点：**
- 从文档列表中移除
- 更新向量索引
- 清除相关缓存
- 返回删除确认

### 1.2 多格式文档解析 ⏱️ 1.5小时
**支持的格式：**
- ✅ TXT（已有）
- ➕ DOCX（Word文档）
- ➕ XLSX（Excel文档）
- ➕ PDF（PDF文档）
- ➕ MD（Markdown文档）

**技术方案：**
```python
# 需要安装的库
python-docx==0.8.11     # Word文档解析
openpyxl==3.0.10        # Excel文档解析
PyPDF2==3.0.1           # PDF文档解析
markdown==3.4.3         # Markdown解析
beautifulsoup4==4.12.2  # HTML清理
```

**实现要点：**
- 创建 `document_parser.py` 模块
- 自动识别文件类型
- 统一转换为文本格式
- 保留元数据（文件名、格式、大小）

### 1.3 外部API集成 ⏱️ 1小时
**功能需求：**
- 从外部API获取文档并添加到知识库
- 支持外部系统调用查询接口
- API认证与权限管理

**新增接口：**
- `POST /api/v1/documents/import-from-api` - 从外部API导入文档
- `POST /api/v1/query-from-external` - 外部系统查询知识库

**实现要点：**
- 支持REST API调用
- 自动解析API响应
- 错误处理与重试机制
- API密钥管理

---

## 🔧 Phase 2: 优化增强（1-2小时）

### 2.1 批量操作接口
- `POST /api/v1/documents/batch-upload` - 批量上传
- `POST /api/v1/documents/batch-delete` - 批量删除
- `POST /api/v1/documents/import-directory` - 导入整个目录

### 2.2 错误处理增强
- 详细的错误信息
- 文件格式验证
- 大小限制检查
- 编码自动检测

### 2.3 API文档更新
- 更新Swagger文档
- 添加使用示例
- 编写API调用指南

---

## 📦 依赖安装

```bash
# 文档解析库
pip install python-docx==0.8.11
pip install openpyxl==3.0.10
pip install PyPDF2==3.0.1
pip install markdown==3.4.3
pip install beautifulsoup4==4.12.2

# HTTP请求库（用于外部API）
pip install httpx==0.25.2
pip install aiohttp==3.9.1
```

---

## 🗂️ 文件结构

```
mPower_Rag/
├── document_parser.py      # 新增：多格式文档解析器
├── external_api.py         # 新增：外部API集成模块
├── simple_api.py          # 修改：添加新接口
├── simple_rag_engine.py   # 修改：支持文档删除
├── requirements.txt       # 更新：添加新依赖
└── tests/
    ├── test_parser.py     # 新增：解析器测试
    └── test_api.py        # 更新：API测试
```

---

## ✅ 验收标准

### 功能验收
- [ ] 可以上传Word/Excel/PDF/MD文档
- [ ] 可以删除单个文档
- [ ] 可以批量删除文档
- [ ] 可以从外部API导入文档
- [ ] 外部系统可以调用查询接口

### 性能验收
- [ ] 文档上传响应时间 <2秒
- [ ] 文档删除响应时间 <1秒
- [ ] 外部API调用响应时间 <3秒

### 文档验收
- [ ] API文档完整
- [ ] 使用示例清晰
- [ ] 错误码说明完整

---

## 📅 时间表

| 时间 | 任务 | 预计时长 |
|------|------|---------|
| 07:45 - 08:15 | 1.1 文档删除功能 | 30分钟 |
| 08:15 - 09:45 | 1.2 多格式文档解析 | 1.5小时 |
| 09:45 - 10:45 | 1.3 外部API集成 | 1小时 |
| 10:45 - 11:00 | 休息 | 15分钟 |
| 11:00 - 12:00 | Phase 2 优化增强 | 1小时 |
| 12:00 - 12:30 | 测试与文档 | 30分钟 |

**总计：约3小时**

---

## 🚀 开始时间：2026-03-05 07:45

*计划制定时间：2026-03-05 07:42*
