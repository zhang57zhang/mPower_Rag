"""
mPower_Rag 评估仪表板
评估结果可视化和分析
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="mPower_Rag 评估仪表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API 配置
API_BASE_URL = "http://localhost:8000/api/v1"


# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #2ecc71;
    }
    .warning-metric {
        border-left-color: #f1c40f;
    }
</style>
""", unsafe_allow_html=True)


# 侧边栏
st.sidebar.title("📊 mPower_Rag 评估")

st.sidebar.markdown("---")
st.sidebar.markdown("### 配置")

dataset_path = st.sidebar.text_input(
    "评估数据集路径",
    value="tests/eval_dataset.json",
    help="JSON 格式的评估数据集"
)

use_rerank = st.sidebar.checkbox(
    "启用重排序",
    value=False,
    help="评估时是否使用重排序功能"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 数据集信息")

# 加载数据集信息
try:
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    metadata = dataset.get("metadata", {})
    data = dataset.get("data", [])
    
    st.sidebar.metric("总问题数", metadata.get("total_questions", 0))
    
    difficulty_dist = metadata.get("difficulty_distribution", {})
    if difficulty_dist:
        st.sidebar.write("**难度分布**:")
        for level, count in difficulty_dist.items():
            st.sidebar.write(f"- {level}: {count}")
    
except FileNotFoundError:
    st.sidebar.error(f"数据集文件不存在: {dataset_path}")
    dataset = {}
    data = []
except Exception as e:
    st.sidebar.error(f"加载数据集失败: {e}")
    dataset = {}
    data = []

st.sidebar.markdown("---")
st.sidebar.markdown("### 操作")

if st.sidebar.button("🚀 开始评估"):
    st.session_state.evaluating = True
    st.rerun()

if st.sidebar.button("📊 查看历史"):
    st.session_state.show_history = True
    st.rerun()


# 主内容区
st.markdown('<p class="main-header">RAG 系统评估仪表板</p>', unsafe_allow_html=True)
st.markdown("---")


# 评估区域
if not st.session_state.get("evaluating", False):
    st.info("点击侧边栏的 '开始评估' 按钮进行评估")
    
    # 显示数据集预览
    if data:
        st.markdown("### 📋 数据集预览")
        st.write(f"总问题数: {len(data)}")
        
        # 显示前 10 个问题
        st.write("**前 10 个问题**:")
        for item in data[:10]:
            st.write(f"- **{item['id']}** ({item['difficulty']}): {item['question']}")
        
        if len(data) > 10:
            st.write(f"... 还有 {len(data) - 10} 个问题")
    
else:
    # 执行评估
    st.markdown("### ⏳ 正在评估...")
    
    try:
        # 调用评估 API
        response = requests.post(
            f"{API_BASE_URL}/evaluate",
            json={"dataset_path": dataset_path, "use_rerank": use_rerank},
            timeout=300,  # 5 分钟超时
        )
        
        if response.status_code == 200:
            result = response.json()
            
            st.success("✅ 评估完成！")
            st.session_state.eval_result = result
            st.session_state.evaluating = False
            st.rerun()
        else:
            st.error(f"❌ 评估失败: {response.status_code}")
            st.session_state.evaluating = False
    
    except Exception as e:
        st.error(f"❌ 评估过程中出错: {e}")
        st.session_state.evaluating = False


# 显示评估结果
if st.session_state.get("eval_result"):
    result = st.session_state.eval_result
    
    st.markdown("---")
    st.markdown("### 📊 评估摘要")
    
    summary = result.get("summary", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均相关性", f"{summary.get('avg_relevance', 0):.2f}", delta="评分")
    
    with col2:
        st.metric("平均准确性", f"{summary.get('avg_accuracy', 0):.2f}", delta="评分")
    
    with col3:
        st.metric("平均完整性", f"{summary.get('avg_completeness', 0):.2f}", delta="评分")
    
    with col4:
        st.metric("平均流畅度", f"{summary.get('avg_fluency', 0):.2f}", delta="评分")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.metric("平均总分", f"{summary.get('avg_overall', 0):.2f}", delta="评分")
    
    with col6:
        st.metric("通过率", f"{summary.get('pass_rate', 0):.1f}%", delta="百分比")
    
    # 通过率颜色
    pass_rate = summary.get('pass_rate', 0)
    if pass_rate >= 80:
        st.markdown('<div class="metric-box success-metric">✅ 优秀：通过率 >= 80%</div>', unsafe_allow_html=True)
    elif pass_rate >= 60:
        st.markdown('<div class="metric-box warning-metric">⚠️ 良好：通过率 60-80%</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-box warning-metric">❌ 需要改进：通过率 < 60%</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 详细结果")
    
    results = result.get("results", [])
    
    if results:
        # 创建 DataFrame
        df_data = []
        for item in results:
            df_data.append({
                "ID": item["id"],
                "问题": item["question"][:50] + "...",
                "类别": item.get("category", ""),
                "难度": item.get("difficulty", ""),
                "相关性": f"{item.get('relevance_score', 0):.2f}",
                "准确性": f"{item.get('accuracy_score', 0):.2f}",
                "完整性": f"{item.get('completeness_score', 0):.2f}",
                "流畅度": f"{item.get('fluency_score', 0):.2f}",
                "总分": f"{item.get('overall_score', 0):.2f}",
                "源文档": item.get("source_count", 0),
            })
        
        df = pd.DataFrame(df_data)
        
        # 显示表格
        st.dataframe(df, use_container_width=True)
        
        # 按总分排序
        df_sorted = df.sort_values("总分", ascending=False)
        
        st.markdown("---")
        st.markdown("### 📊 分数分布")
        
        # 分数直方图
        fig = px.histogram(
            df,
            x="总分",
            nbins=20,
            title="总分分布",
            color_discrete_sequence=["blue"]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 难度 vs 总分
        fig = px.box(
            df,
            x="难度",
            y="总分",
            title="难度 vs 总分",
            color="难度"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 类别平均分
        fig = px.bar(
            df.groupby("类别").mean().reset_index(),
            x="类别",
            y=["相关性", "准确性", "完整性", "流畅度", "总分"],
            title="各类别平均分",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("没有评估结果")


# 历史评估
if st.session_state.get("show_history"):
    st.markdown("---")
    st.markdown("### 📚 评估历史")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/evaluations",
            timeout=10,
        )
        
        if response.status_code == 200:
            history = response.json()
            st.json(history)
        else:
            st.error(f"获取历史失败: {response.status_code}")
    
    except Exception as e:
        st.error(f"获取历史出错: {e}")
    
    st.session_state.show_history = False


# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "mPower_Rag 评估仪表板 v0.1.0"
    "</div>",
    unsafe_allow_html=True,
)
