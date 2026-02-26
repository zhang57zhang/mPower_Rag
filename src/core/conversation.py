"""
对话管理模块
支持多轮对话、会话历史、上下文维护
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConversationManager:
    """对话管理器"""

    def __init__(self, max_history: int = 10):
        """
        初始化对话管理器

        Args:
            max_history: 最大历史记录数量
        """
        self.max_history = max_history
        self.conversations: Dict[str, Dict[str, Any]] = {}

    def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        创建新对话

        Args:
            conversation_id: 对话 ID（可选，自动生成）
            metadata: 元数据

        Returns:
            对话 ID
        """
        if conversation_id is None:
            conversation_id = f"conv_{datetime.now().timestamp()}"

        self.conversations[conversation_id] = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "messages": [],
            "context": {},
        }

        logger.info(f"创建对话: {conversation_id}")
        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        添加消息到对话

        Args:
            conversation_id: 对话 ID
            role: 角色（user/assistant/system）
            content: 消息内容
            metadata: 消息元数据
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"对话不存在: {conversation_id}")

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.conversations[conversation_id]["messages"].append(message)
        self.conversations[conversation_id]["updated_at"] = datetime.now().isoformat()

        # 限制历史记录数量
        if len(self.conversations[conversation_id]["messages"]) > self.max_history:
            # 保留系统消息和最近的用户/助手消息
            messages = self.conversations[conversation_id]["messages"]
            system_messages = [m for m in messages if m["role"] == "system"]
            recent_messages = messages[-self.max_history:]
            self.conversations[conversation_id]["messages"] = system_messages + recent_messages

        logger.debug(f"添加消息到对话 {conversation_id}: {role}")

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        获取对话

        Args:
            conversation_id: 对话 ID

        Returns:
            对话数据
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"对话不存在: {conversation_id}")
        return self.conversations[conversation_id].copy()

    def get_history(
        self,
        conversation_id: str,
        include_system: bool = False,
    ) -> List[Dict[str, str]]:
        """
        获取对话历史（用于 LLM）

        Args:
            conversation_id: 对话 ID
            include_system: 是否包含系统消息

        Returns:
            消息列表
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"对话不存在: {conversation_id}")

        messages = self.conversations[conversation_id]["messages"]

        if not include_system:
            messages = [m for m in messages if m["role"] != "system"]

        # 转换为 LLM 格式
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]

        return history

    def update_context(
        self,
        conversation_id: str,
        context: Dict[str, Any],
    ) -> None:
        """
        更新对话上下文

        Args:
            conversation_id: 对话 ID
            context: 上下文数据
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"对话不存在: {conversation_id}")

        self.conversations[conversation_id]["context"].update(context)
        self.conversations[conversation_id]["updated_at"] = datetime.now().isoformat()

        logger.debug(f"更新对话上下文 {conversation_id}")

    def clear_conversation(self, conversation_id: str) -> None:
        """
        清空对话消息

        Args:
            conversation_id: 对话 ID
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"对话不存在: {conversation_id}")

        self.conversations[conversation_id]["messages"] = []
        self.conversations[conversation_id]["updated_at"] = datetime.now().isoformat()

        logger.info(f"清空对话: {conversation_id}")

    def delete_conversation(self, conversation_id: str) -> None:
        """
        删除对话

        Args:
            conversation_id: 对话 ID
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"对话不存在: {conversation_id}")

        del self.conversations[conversation_id]
        logger.info(f"删除对话: {conversation_id}")

    def list_conversations(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        列出所有对话

        Args:
            limit: 最大返回数量

        Returns:
            对话列表
        """
        conversations = list(self.conversations.values())

        # 按更新时间排序
        conversations.sort(
            key=lambda x: x["updated_at"],
            reverse=True,
        )

        return conversations[:limit]

    def get_conversation_summary(
        self,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        获取对话摘要

        Args:
            conversation_id: 对话 ID

        Returns:
            摘要信息
        """
        conv = self.get_conversation(conversation_id)

        return {
            "id": conv["id"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "message_count": len(conv["messages"]),
            "metadata": conv["metadata"],
            "context": conv["context"],
        }


# 全局对话管理器实例
_conversation_manager = None


def get_conversation_manager(max_history: int = 10) -> ConversationManager:
    """获取对话管理器（单例）"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager(max_history=max_history)
    return _conversation_manager
