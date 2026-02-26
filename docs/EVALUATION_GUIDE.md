# 评估功能使用指南

**版本**: 1.0
**最后更新**: 2026-02-23

---

## 📋 功能概述

mPower_Rag 的评估功能可以帮助你：
- 📊 量化 RAG 系统性能
- 📈 可视化评估结果
- 🔍 识别系统弱点和改进方向
- 📝 生成详细的评估报告

---

## 🎯 评估指标

### 检索指标
1. **相关性 (Relevance)**
   - 检索到的文档与查询的相关程度
   - 范围：0.0 - 1.0，越高越好
   - 计算：基于检索文档和查询的语义相似度

2. **准确性 (Accuracy)**
   - 生成答案与标准答案的匹配程度
   - 范围：0.0 - 1.0，越高越好
   - 计算：基于答案的关键词和语义匹配

### 生成指标
3. **完整性 (Completeness)**
   - 答案是否完整回答了问题
   - 范围：0.0 - 1.0，越高越好
   - 计算：基于答案覆盖问题的程度

4. **流畅度 (Fluency)**
   - 答案的语言流畅程度和可读性
   - 范围：0.0 - 1.0，越高越好
   - 计算：基于句法和语义质量

5. **总分 (Overall)**
   - 综合评分，反映系统整体性能
   - 范围：0.0 - 1.0，越高越好
   - 计算：相关性、准确性、完整性、流畅度的加权平均

---

## 🏗️ 架构设计

### 评估流程

```
加载评估数据集
    ↓
执行 RAG 查询（每个问题）
    ↓
收集查询结果和源文档
    ↓
计算各项评估指标
    ↓
生成评估报告
    ↓
可视化展示结果
```

### 代码架构

```
tests/eval_dataset.json  # 评估数据集
    ↓
src/core/evaluation.py  # 评估器实现
    ↓
src/api/main.py  # 评估 API 接口
    ↓
frontend/evaluation.py  # 评估仪表板
```

---

## 📊 数据集格式

### JSON 结构

```json
{
  "dataset_name": "mPower_Rag 评估数据集",
  "version": "1.0",
  "description": "车载测试 RAG 系统评估数据集",
  "data": [
    {
      "id": 1,
      "question": "用户问题",
      "category": "类别",
      "difficulty": "难度",
      "expected_answer": "标准答案",
      "related_docs": ["相关文档1", "相关文档2"],
      "keywords": ["关键词1", "关键词2"]
    },
    ...
  ],
  "metadata": {
    "total_questions": 10,
    "categories": ["类别1", "类别2"],
    "difficulty_distribution": {
      "简单": 3,
      "中等": 4,
      "困难": 3
    }
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | int | 问题唯一标识 | 1 |
| `question` | string | 用户问题 | "什么是车载测试？" |
| `category` | string | 问题类别 | "基础概念" |
| `difficulty` | string | 难度等级 | "简单"、"中等"、"困难" |
| `expected_answer` | string | 标准答案 | "车载测试是指..." |
| `related_docs` | array | 相关文档列表 | ["车载测试基础"] |
| `keywords` | array | 关键词列表 | ["车载测试", "定义"] |

---

## 🚀 使用指南

### 1. 准备评估数据集

#### 创建数据集文件

```bash
# 在项目根目录下
touch tests/eval_dataset.json
```

#### 编辑数据集

添加测试问题、类别、难度和标准答案。

**提示**：
- 涵盖不同类别的问题
- 包含不同难度的问题
- 标准答案应该详细和准确
- 标注相关文档和关键词

### 2. 启动评估仪表板

#### 方法 1：直接启动

```bash
# 激活虚拟环境
.\venv311\Scripts\Activate

# 启动仪表板
streamlit run frontend/evaluation.py --server.port 8502
```

#### 方法 2：使用 API

```bash
# 执行评估
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "tests/eval_dataset.json",
    "use_rerank": false
  }'

# 查看历史
curl http://localhost:8000/api/v1/evaluations

# 查看统计
curl http://localhost:8000/api/v1/evaluations/stats
```

### 3. 配置评估参数

#### 数据集路径

在仪表板侧边栏中配置：
- 默认：`tests/eval_dataset.json`
- 可以自定义路径

#### 启用重排序

勾选"启用重排序"复选框，可以：
- 测试重排序对检索质量的影响
- 对比有/无重排序的性能

---

## 📈 评估结果解读

### 评分标准

| 分数范围 | 评价 | 说明 |
|---------|------|------|
| 0.9 - 1.0 | 优秀 | 系统表现非常好 |
| 0.7 - 0.9 | 良好 | 系统表现良好 |
| 0.5 - 0.7 | 一般 | 系统表现一般，需要改进 |
| 0.3 - 0.5 | 较差 | 系统表现较差，急需改进 |
| 0.0 - 0.3 | 很差 | 系统表现很差，严重问题 |

### 指标说明

#### 相关性
- **低 (0.0 - 0.5)**: 检索到的文档与查询不相关
- **中 (0.5 - 0.7)**: 检索到的文档部分相关
- **高 (0.7 - 1.0)**: 检索到的文档高度相关

#### 准确性
- **低 (0.0 - 0.5)**: 答案与标准答案差距很大
- **中 (0.5 - 0.7)**: 答案部分正确，但有关键信息错误
- **高 (0.7 - 1.0)**: 答案与标准答案基本一致

#### 完整性
- **低 (0.0 - 0.5)**: 答案不完整，缺少重要信息
- **中 (0.5 - 0.7)**: 答案基本完整，但有些细节缺失
- **高 (0.7 - 1.0)**: 答案完整，覆盖所有要点

#### 流畅度
- **低 (0.0 - 0.5)**: 答案语言不通顺，难以理解
- **中 (0.5 - 0.7)**: 答案基本通顺，但有些表达问题
- **高 (0.7 - 1.0)**: 答案语言通顺，表达清晰

---

## 🎨 仪表板功能

### 1. 评估摘要

显示关键指标：
- 平均相关性
- 平均准确性
- 平均完整性
- 平均流畅度
- 平均总分
- 通过率

### 2. 详细结果

表格显示每个问题的评估结果：
- ID
- 问题（前 50 字符）
- 类别
- 难度
- 相关性、准确性、完整性、流畅度、总分
- 源文档数量

### 3. 可视化图表

#### 分数分布直方图
- 显示总分分布情况
- 了解系统性能分布

#### 难度 vs 总分箱线图
- 显示不同难度问题的得分情况
- 识别问题点

#### 各别平均分柱状图
- 显示不同类别的平均分
- 了解不同领域的表现

---

## 🔧 高级功能

### 1. 对比评估

可以评估不同配置的 performance：

#### 对比有无重排序

```bash
# 不使用重排序
curl -X POST http://localhost:8000/api/v1/evaluate \
  -d '{"dataset_path": "tests/eval_dataset.json", "use_rerank": false}'

# 使用重排序
curl -X POST http://localhost:8000/api/v1/evaluate \
  -d '{"dataset_path": "tests/eval_dataset.json", "use_rerank": true}'
```

#### 对比不同 Top K

```bash
# Top 5
curl -X POST http://localhost:8000/api/v1/evaluate \
  -d '{"dataset_path": "tests/eval_dataset.json", "top_k": 5}'

# Top 10
curl -X POST http://localhost:8000/api/v1/evaluate \
  -d '{"dataset_path": "tests/eval_dataset.json", "top_k": 10}'
```

### 2. 导出评估结果

#### 导出为 CSV

```python
import pandas as pd

# 假设评估结果在 result 变量中
df = pd.DataFrame(result["results"])
df.to_csv("evaluation_results.csv", index=False)
```

#### 导出为 JSON

```python
import json

with open("evaluation_results.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

### 3. 自动化评估

#### 使用脚本

```bash
python scripts/test_evaluation.py
```

#### 集成到 CI/CD

```yaml
# .github/workflows/evaluation.yml
name: RAG 评估

on: [push]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: 设置 Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: 安装依赖
        run: pip install -r requirements.txt
      - name: 启动服务
        run: docker-compose up -d qdrant
      - name: 运行评估
        run: python scripts/test_evaluation.py
```

---

## 📝 最佳实践

### 1. 数据集设计

**包含的问题类型**:
- 基础概念
- 测试流程
- 故障诊断
- 技术标准
- 使用场景

**难度分布**:
- 30% 简单
- 50% 中等
- 20% 困难

### 2. 评估频率

**建议频率**:
- 每次重大更新后评估
- 每周定期评估
- 上线前评估

### 3. 结果分析

**关注指标**:
- 总分 < 0.6：需要改进
- 相关性 < 0.7：检索质量差
- 准确性 < 0.7：生成质量差
- 通过率 < 60%：需要优化

### 4. 改进方向

**根据评估结果**:
- 相关性低 → 优化嵌入模型或重排序
- 准确性低 → 优化 Prompt 或 LLM
- 完整性低 → 优化检索策略或上下文
- 流畅度低 → 优化生成参数或模型

---

## 🆘 常见问题

### Q: 如何提高评估分数？
A: 根据具体指标进行优化：
- 相关性低 → 使用重排序、优化嵌入模型
- 准确性低 → 优化 Prompt、尝试更好的 LLM
- 完整性低 → 检索更多文档、优化上下文
- 流畅度低 → 调整 temperature、max_tokens

### Q: 评估很慢怎么办？
A: 优化方法：
- 减少数据集大小（先测试少量问题）
- 使用更快的模型
- 并行评估（如果支持）
- 缓存检索结果

### Q: 如何创建好的评估数据集？
A: 建议方法：
- 涵盖不同类别和难度
- 标准答案要详细和准确
- 标注相关文档和关键词
- 逐步扩充数据集

### Q: 通过率很低怎么办？
A: 分析原因：
- 查看具体哪些问题未通过
- 分析失败原因（相关性、准确性等）
- 针对性地优化
- 调整评分标准（如果过严）

---

## 📚 参考资料

### 评估方法论
- [RAGAS - RAG 评估框架](https://docs.ragas.io/en/stable/)
- [TruLens - RAG 可靠性评估](https://www.trulens.org/)
- [DeepEval - LLM 评估框架](https://deepeval.ai/)

### 评估指标
- [Precision、Recall、F1](https://en.wikipedia.org/wiki/Precision_and_recall)
- [MRR (Mean Reciprocal Rank)](https://en.wikipedia.org/wiki/Mean_reciprocal_rank)
- [NDCG (Normalized Discounted Cumulative Gain)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)

### 可视化
- [Plotly Python](https://plotly.com/python/)
- [Streamlit 文档](https://docs.streamlit.io/)

---

## 🎯 下一步

### 功能改进
- [ ] 添加更多评估指标
- [ ] 支持自定义评估标准
- [ ] 添加评估结果对比功能
- [ ] 支持评估历史趋势分析

### 用户体验
- [ ] 优化仪表板界面
- [ ] 添加导出功能
- [ ] 添加分享功能
- [ ] 添加评论功能

---

**最后更新**: 2026-02-23
**版本**: 1.0
**维护者**: AI 助手
