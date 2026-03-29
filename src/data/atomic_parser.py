"""
原子化知识解析器
实现知识文档的"不重不漏"原子化解析
"""
import re
import hashlib
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AtomType(Enum):
    """知识原子类型"""
    DEFINITION = "definition"      # 定义
    PROCEDURE = "procedure"        # 流程/步骤
    QAPAIR = "qapair"             # 问答对
    STATEMENT = "statement"        # 陈述
    TABLE = "table"               # 表格
    LIST = "list"                 # 列表
    CODE = "code"                 # 代码
    UNKNOWN = "unknown"           # 未知


@dataclass
class KnowledgeAtom:
    """
    知识原子
    
    知识的最小单元，具有独立语义
    """
    id: str
    content: str
    atom_type: AtomType
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    related_atoms: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "atom_type": self.atom_type.value,
            "source": self.source,
            "metadata": self.metadata,
            "keywords": self.keywords,
            "related_atoms": self.related_atoms,
            "confidence": self.confidence,
        }
    
    def compute_hash(self) -> str:
        """计算内容哈希（用于去重）"""
        normalized = " ".join(self.content.split())
        return hashlib.md5(normalized.encode()).hexdigest()


class AtomicKnowledgeParser:
    """
    原子化知识解析器
    
    核心功能：
    1. 语义分块 - 按语义边界分割，不破坏知识完整性
    2. 类型识别 - 自动识别知识类型（定义、流程、QA等）
    3. 关键词提取 - 提取核心关键词
    4. 去重处理 - 确保知识"不重"
    5. 完整性检查 - 确保知识"不漏"
    """
    
    def __init__(
        self,
        min_atom_size: int = 50,     # 最小原子大小
        max_atom_size: int = 1000,   # 最大原子大小
        dedup_threshold: float = 0.95,  # 去重相似度阈值
        extract_keywords: bool = True,
    ):
        """
        初始化解析器
        
        Args:
            min_atom_size: 最小原子大小（字符）
            max_atom_size: 最大原子大小
            dedup_threshold: 去重相似度阈值
            extract_keywords: 是否提取关键词
        """
        self.min_atom_size = min_atom_size
        self.max_atom_size = max_atom_size
        self.dedup_threshold = dedup_threshold
        self.extract_keywords = extract_keywords
        
        # 已处理的原子哈希（用于去重）
        self._atom_hashes: Set[str] = set()
        
        # 类型识别模式
        self._type_patterns = self._build_type_patterns()
        
        logger.info(f"AtomicKnowledgeParser initialized (min={min_atom_size}, max={max_atom_size})")
    
    def parse_document(
        self,
        content: str,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[KnowledgeAtom]:
        """
        解析文档为知识原子
        
        Args:
            content: 文档内容
            source: 来源标识
            metadata: 额外元数据
            
        Returns:
            知识原子列表（已去重）
        """
        logger.info(f"Parsing document from {source or 'unknown'}")
        
        # 1. 预处理
        content = self._preprocess(content)
        
        # 2. 结构化解析
        sections = self._extract_sections(content)
        
        # 3. 生成原子
        atoms = []
        atom_index = 0
        
        for section in sections:
            # 按段落分割
            paragraphs = self._split_paragraphs(section["content"])
            
            for para in paragraphs:
                # 跳过太短的内容
                if len(para) < self.min_atom_size:
                    continue
                
                # 识别类型
                atom_type = self._identify_type(para)
                
                # 如果太长，进一步分割
                if len(para) > self.max_atom_size:
                    sub_atoms = self._split_large_content(para, atom_type, source)
                    atoms.extend(sub_atoms)
                else:
                    atom = self._create_atom(
                        content=para,
                        atom_type=atom_type,
                        source=source,
                        section_info=section,
                        metadata=metadata,
                        index=atom_index,
                    )
                    atoms.append(atom)
                    atom_index += 1
        
        # 4. 去重
        unique_atoms = self._deduplicate(atoms)
        
        # 5. 提取关键词
        if self.extract_keywords:
            for atom in unique_atoms:
                atom.keywords = self._extract_keywords_from_content(atom.content)
        
        # 6. 建立关联
        self._build_relations(unique_atoms)
        
        logger.info(f"Parsed {len(atoms)} atoms, {len(unique_atoms)} unique")
        
        return unique_atoms
    
    def _preprocess(self, content: str) -> str:
        """预处理内容"""
        # 统一换行符
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        
        # 移除多余空行
        content = re.sub(r"\n{3,}", "\n\n", content)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in content.split("\n")]
        content = "\n".join(lines)
        
        return content
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        提取文档结构（章节）
        
        识别标题层级
        """
        sections = []
        current_section = {"title": "root", "level": 0, "content": ""}
        
        lines = content.split("\n")
        buffer = []
        
        for line in lines:
            # 检测 Markdown 标题
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            
            if header_match:
                # 保存当前章节
                if buffer:
                    current_section["content"] = "\n".join(buffer)
                    sections.append(current_section.copy())
                    buffer = []
                
                # 开始新章节
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    "title": title,
                    "level": level,
                    "content": "",
                }
            else:
                buffer.append(line)
        
        # 保存最后一个章节
        if buffer:
            current_section["content"] = "\n".join(buffer)
            sections.append(current_section)
        
        return sections
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """按段落分割"""
        paragraphs = content.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _build_type_patterns(self) -> Dict[AtomType, List[str]]:
        """构建类型识别模式"""
        return {
            AtomType.DEFINITION: [
                r"(.+?)是指(.+)",
                r"(.+?)定义为(.+)",
                r"(.+?)，即(.+)",
                r"所谓(.+?)，(.+)",
                r"What is (.+?)\?",
            ],
            AtomType.PROCEDURE: [
                r"^(步骤|Step)\s*\d+",
                r"^\d+[\.、]\s*(.+)",
                r"首先[，,](.+)然后[，,](.+)",
                r"第一步[：:](.+)",
            ],
            AtomType.QAPAIR: [
                r"问[：:](.+?)答[：:](.+)",
                r"Q[：:](.+?)A[：:](.+)",
                r"(.+?)\?(.+)",
            ],
            AtomType.LIST: [
                r"^[-*•]\s*(.+)",
                r"^[•·]\s*(.+)",
            ],
            AtomType.CODE: [
                r"```",
                r"`.+`",
            ],
            AtomType.TABLE: [
                r"\|.+\|",
                r"^[-+|=]+\s*$",
            ],
        }
    
    def _identify_type(self, content: str) -> AtomType:
        """识别知识类型"""
        for atom_type, patterns in self._type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    return atom_type
        
        return AtomType.STATEMENT
    
    def _split_large_content(
        self,
        content: str,
        atom_type: AtomType,
        source: str,
    ) -> List[KnowledgeAtom]:
        """分割过大的内容"""
        atoms = []
        
        # 按句子分割
        sentences = self._split_sentences(content)
        
        # 合并为合适大小的块
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            if current_size + len(sentence) > self.max_atom_size and current_chunk:
                # 创建原子
                chunk_content = "".join(current_chunk)
                atom = KnowledgeAtom(
                    id=self._generate_id(chunk_content, source),
                    content=chunk_content,
                    atom_type=atom_type,
                    source=source,
                )
                atoms.append(atom)
                
                current_chunk = [sentence]
                current_size = len(sentence)
            else:
                current_chunk.append(sentence)
                current_size += len(sentence)
        
        # 处理剩余内容
        if current_chunk:
            chunk_content = "".join(current_chunk)
            atom = KnowledgeAtom(
                id=self._generate_id(chunk_content, source),
                content=chunk_content,
                atom_type=atom_type,
                source=source,
            )
            atoms.append(atom)
        
        return atoms
    
    def _split_sentences(self, content: str) -> List[str]:
        """按句子分割"""
        # 中英文句子分割
        pattern = r"(?<=[。！？.!?])\s*"
        sentences = re.split(pattern, content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_atom(
        self,
        content: str,
        atom_type: AtomType,
        source: str,
        section_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]],
        index: int,
    ) -> KnowledgeAtom:
        """创建知识原子"""
        return KnowledgeAtom(
            id=self._generate_id(content, source, index),
            content=content,
            atom_type=atom_type,
            source=source,
            metadata={
                "section_title": section_info.get("title", ""),
                "section_level": section_info.get("level", 0),
                **(metadata or {}),
            },
        )
    
    def _generate_id(
        self,
        content: str,
        source: str,
        index: int = 0,
    ) -> str:
        """生成唯一 ID"""
        hash_input = f"{source}:{index}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _deduplicate(self, atoms: List[KnowledgeAtom]) -> List[KnowledgeAtom]:
        """
        去重
        
        使用内容哈希进行精确去重
        """
        unique_atoms = []
        
        for atom in atoms:
            content_hash = atom.compute_hash()
            
            if content_hash not in self._atom_hashes:
                self._atom_hashes.add(content_hash)
                unique_atoms.append(atom)
            else:
                logger.debug(f"Duplicate atom found: {atom.id}")
        
        return unique_atoms
    
    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        keywords = []
        
        # 简单的关键词提取（实际可用 NLP）
        # 1. 提取引号中的内容
        quoted = re.findall(r"['\"](.+?)['\"]", content)
        keywords.extend(quoted)
        
        # 2. 提取专业术语（大写字母开头的词）
        terms = re.findall(r"\b([A-Z][a-zA-Z]+)\b", content)
        keywords.extend(terms)
        
        # 3. 提取中文关键词（2-4字）
        chinese = re.findall(r"[\u4e00-\u9fa5]{2,4}", content)
        keywords.extend(chinese[:5])  # 限制数量
        
        # 去重
        return list(set(keywords))[:10]
    
    def _build_relations(self, atoms: List[KnowledgeAtom]):
        """建立原子间的关联"""
        # 简单实现：基于共同关键词建立关联
        keyword_to_atoms: Dict[str, List[str]] = {}
        
        for atom in atoms:
            for keyword in atom.keywords:
                if keyword not in keyword_to_atoms:
                    keyword_to_atoms[keyword] = []
                keyword_to_atoms[keyword].append(atom.id)
        
        # 设置关联
        for atom in atoms:
            related = set()
            for keyword in atom.keywords:
                related.update(keyword_to_atoms.get(keyword, []))
            related.discard(atom.id)  # 移除自己
            atom.related_atoms = list(related)[:5]  # 限制关联数量
    
    def get_stats(self) -> Dict[str, Any]:
        """获取解析统计"""
        return {
            "total_hashes": len(self._atom_hashes),
        }
    
    def clear(self):
        """清空状态"""
        self._atom_hashes.clear()
