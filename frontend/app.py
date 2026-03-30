"""
mPower_Rag 前端应用
基于 Streamlit 实现
"""
import streamlit as st
import requests
from typing import List, Dict, Any
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="mPower_Rag - 车载测试系统",
    page_icon="🚗",
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
    }
    .query-input {
        padding: 10px;
        border: 2px solid #1f77b4;
        border-radius: 5px;
        font-size: 1.1rem;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .source-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        border-left: 4px solid #1f77b4;
    }
    /* 聊天消息样式 */
    .user-message {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #bbdefb;
    }
    .assistant-message {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
    /* 隐藏 Streamlit 默认的底部空白 */
    .block-container {
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def query_rag(question: str, top_k: int = 5) -> Dict[str, Any]:
    """
    调用 RAG API 查询

    Args:
        question: 用户问题
        top_k: 返回文档数量

    Returns:
        API 响应
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": question, "top_k": top_k},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API 调用失败: {e}")
        return {
            "answer": f"API 调用失败：{str(e)}",
            "question": question,
            "source_documents": [],
        }


def search_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    搜索文档

    Args:
        query: 搜索关键词
        top_k: 返回结果数量

    Returns:
        搜索结果列表
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/search",
            params={"query": query, "top_k": top_k},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"搜索失败: {e}")
        return []


# 对话管理 API 函数


def create_conversation(metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """创建新对话"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversations",
            json={"metadata": metadata or {}},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"创建对话失败: {e}")
        return {"conversation_id": None, "message": str(e)}


def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """获取对话详情"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/conversations/{conversation_id}",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"获取对话失败: {e}")
        return None


def send_message(conversation_id: str, question: str, top_k: int = 5, use_history: bool = True) -> Dict[str, Any]:
    """发送消息到对话"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversations/{conversation_id}/messages",
            json={"question": question, "top_k": top_k, "use_history": use_history},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"发送消息失败: {e}")
        return {
            "answer": f"API 调用失败：{str(e)}",
            "question": question,
            "source_documents": [],
            "conversation_id": conversation_id,
        }


def list_conversations(limit: int = 20) -> List[Dict[str, Any]]:
    """列出所有对话"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/conversations",
            params={"limit": limit},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("conversations", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"列出对话失败: {e}")
        return []


def delete_conversation(conversation_id: str) -> bool:
    """删除对话"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/conversations/{conversation_id}",
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"删除对话失败: {e}")
        return False


def main():
    """主函数"""
    # 初始化 session state
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 侧边栏
    st.sidebar.title("🚗 mPower_Rag")
    st.sidebar.markdown("---")

    # 模式选择
    mode = st.sidebar.radio(
        "选择模式",
        ["💬 智能问答", "🔍 文档搜索", "📁 知识管理"],
    )

    # 智能问答模式下的对话历史
    if mode == "💬 智能问答":
        st.sidebar.markdown("### 对话历史")

        # 新建对话按钮
        if st.sidebar.button("➕ 新建对话"):
            result = create_conversation()
            if result.get("conversation_id"):
                st.session_state.current_conversation_id = result["conversation_id"]
                st.session_state.chat_history = []
                st.rerun()

        # 对话列表
        conversations = list_conversations(limit=20)
        if conversations:
            for conv in conversations:
                conv_id = conv["id"]
                conv_title = f"对话 {conv_id[-6:]} ({conv['message_count']} 条消息)"

                # 创建两列：对话名和删除按钮
                col1, col2 = st.sidebar.columns([4, 1])

                with col1:
                    if st.button(
                        conv_title,
                        key=f"conv_{conv_id}",
                        use_container_width=True,
                    ):
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.chat_history = conv.get("messages", [])
                        st.rerun()

                with col2:
                    if st.button("🗑️", key=f"del_{conv_id}"):
                        if delete_conversation(conv_id):
                            if st.session_state.current_conversation_id == conv_id:
                                st.session_state.current_conversation_id = None
                                st.session_state.chat_history = []
                            st.rerun()
        else:
            st.sidebar.info("暂无对话历史")

        st.sidebar.markdown("---")

    # 配置参数
    st.sidebar.markdown("### 配置")
    top_k = st.sidebar.slider("返回文档数量", 1, 10, 5)
    use_rerank = st.sidebar.checkbox("启用重排序", value=False, help="使用重排序提高检索准确性")
    st.sidebar.markdown("---")

    # 统计信息
    st.sidebar.markdown("### 系统信息")
    try:
        stats_response = requests.get(f"{API_BASE_URL}/documents/stats", timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            st.sidebar.metric("文档总数", stats.get("total_documents", 0))
            st.sidebar.metric("知识块总数", stats.get("total_chunks", 0))
    except:
        st.sidebar.write("无法获取统计信息")

    # 主内容区
    if mode == "💬 智能问答":
        # 显示当前对话标题
        if st.session_state.current_conversation_id:
            st.markdown(f'<p class="main-header">智能问答 - 对话 {st.session_state.current_conversation_id[-6:]}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="main-header">智能问答</p>', unsafe_allow_html=True)
        st.markdown("---")

        # 创建对话容器，用于显示对话历史
        chat_container = st.container()

        # 显示对话历史
        with chat_container:
            for i, msg in enumerate(st.session_state.chat_history):
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "user":
                    # 用户消息
                    st.markdown(f'<div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;">', unsafe_allow_html=True)
                    st.markdown(f"**👤 用户**")
                    st.markdown(content)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # 助手消息
                    st.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">', unsafe_allow_html=True)
                    st.markdown(f"**🤖 助手**")
                    st.markdown(content)
                    st.markdown('</div>', unsafe_allow_html=True)

        # 示例问题（只在没有对话历史时显示）
        if not st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 示例问题")
            example_questions = [
                "如何测试车载蓝牙模块的连接稳定性？",
                "车载 CAN 总线测试的标准流程是什么？",
                "如何诊断车载电源系统的故障？",
            ]
            cols = st.columns(len(example_questions))
            for i, question in enumerate(example_questions):
                if cols[i].button(question, key=f"example_{i}"):
                    st.session_state.user_question = question
                    st.rerun()

        # 用户输入区域
        st.markdown("---")
        st.markdown("### 提问")

        # 创建输入和发送按钮的列布局
        col1, col2 = st.columns([5, 1])

        with col1:
            user_question = st.text_area(
                "请输入您的问题",
                value=st.session_state.get("user_question", ""),
                height=80,
                key="query_input",
                label_visibility="collapsed",
            )

        with col2:
            st.write("")  # 占位符，用于对齐
            send_button = st.button("🚀 发送", type="primary", use_container_width=True)

        # 发送消息
        if send_button or (user_question.strip() and st.session_state.user_question != ""):
            if not user_question.strip():
                st.warning("请输入问题")
            else:
                # 如果没有对话，创建新对话
                if not st.session_state.current_conversation_id:
                    result = create_conversation()
                    if result.get("conversation_id"):
                        st.session_state.current_conversation_id = result["conversation_id"]
                    else:
                        st.error("创建对话失败")
                        st.stop()

                # 添加用户消息到历史
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question,
                })

                with st.spinner("正在思考..."):
                    # 发送消息到对话 API（传递重排序参数）
                    result = send_message(
                        conversation_id=st.session_state.current_conversation_id,
                        question=user_question,
                        top_k=top_k,
                        use_history=True,
                    )

                    # 添加助手回复到历史
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result.get("answer", "抱歉，没有获得回答"),
                    })

                    # 清空输入
                    st.session_state.user_question = ""

                    # 重新运行以显示更新
                    st.rerun()

        # 显示源文档（如果有最新的回答）
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
            # 这里可以添加显示源文档的逻辑
            # 需要从 API 返回中获取源文档
            pass

    elif mode == "🔍 文档搜索":
        st.markdown('<p class="main-header">文档搜索</p>', unsafe_allow_html=True)
        st.markdown("---")

        # 搜索输入
        search_query = st.text_input(
            "搜索关键词",
            placeholder="输入关键词搜索相关文档...",
            key="search_input",
        )

        # 搜索按钮
        if st.button("🔍 搜索") and search_query:
            with st.spinner("正在搜索..."):
                results = search_documents(search_query, top_k)

                if results:
                    st.markdown(f"找到 **{len(results)}** 个相关文档")
                    st.markdown("---")

                    for i, doc in enumerate(results, 1):
                        st.markdown(f"### 结果 {i}")
                        st.markdown(doc.get('content', ''))
                        st.markdown(f"**相似度:** {doc.get('score', 0):.3f}")
                        if doc.get('metadata'):
                            with st.expander("查看元数据"):
                                st.json(doc.get('metadata', {}))
                        st.markdown("---")
                else:
                    st.info("未找到相关文档")

    elif mode == "📁 知识管理":
        st.markdown('<p class="main-header">知识管理</p>', unsafe_allow_html=True)
        st.markdown("---")

        # 文件上传
        st.markdown("### 上传文档")
        uploaded_files = st.file_uploader(
            "上传文档到知识库",
            type=["pdf", "docx", "xlsx", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(
                        f"{API_BASE_URL}/documents/upload",
                        files=files,
                        timeout=120,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {uploaded_file.name} 上传成功")
                        st.info(f"生成 {result.get('chunk_count', 0)} 个知识块")
                    else:
                        st.error(f"❌ {uploaded_file.name} 上传失败")
                except Exception as e:
                    st.error(f"上传错误: {e}")

        # 知识库管理
        st.markdown("### 知识库操作")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 刷新统计"):
                st.rerun()

        with col2:
            if st.button("🗑️ 清空知识库"):
                st.warning("⚠️ 此操作不可逆，将删除所有知识块！")
                # 使用 session_state 来确认删除
                if 'confirm_clear' not in st.session_state:
                    st.session_state.confirm_clear = False
                
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button("✅ 确认清空"):
                        try:
                            response = requests.post(f"{API_BASE_URL}/cache/clear_all", timeout=30)
                            if response.status_code == 200:
                                st.success("知识库已清空")
                            else:
                                st.error(f"清空失败: {response.text}")
                        except Exception as e:
                            st.error(f"清空错误: {e}")
                with col_confirm2:
                    if st.button("❌ 取消"):
                        st.info("已取消")

    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "mPower_Rag v0.1.0 - 车载测试系统 RAG"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
