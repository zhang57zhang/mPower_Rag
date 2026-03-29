"""
数据处理模块
提供文档加载、解析、分块等功能
"""
from .document_loader import get_document_manager, DocumentManager
from .enhanced_loader import get_enhanced_loader, EnhancedDocumentLoader
from .atomic_parser import AtomicKnowledgeParser, KnowledgeAtom
from .deduplication import DeduplicationManager

__all__ = [
    'get_document_manager',
    'DocumentManager',
    'get_enhanced_loader',
    'EnhancedDocumentLoader',
    'AtomicKnowledgeParser',
    'KnowledgeAtom',
    'DeduplicationManager',
]
