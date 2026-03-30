"""
RAG 评估模块
提供检索和生成的评估指标
"""
from typing import List, Dict, Any, Optional, Tuple, Iterator
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetrievalMetrics:
    """检索评估指标"""
    precision: float
    recall: float
    f1: float
    mrr: float  # Mean Reciprocal Rank
    ndcg: float  # Normalized Discounted Cumulative Gain


@dataclass
class GenerationMetrics:
    """生成评估指标"""
    relevance: float  # 相关性
    accuracy: float  # 准确性
    completeness: float  # 完整性
    fluency: float  # 流利度


class RAGEvaluator:
    """RAG 评估器"""

    def __init__(self):
        """初始化评估器"""
        self.evaluations: List[Dict[str, Any]] = []

    def evaluate_retrieval(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        k: int = 5,
    ) -> RetrievalMetrics:
        """
        评估检索质量

        Args:
            retrieved_docs: 检索到的文档
            relevant_docs: 相关文档
            k: 考虑的前 k 个结果

        Returns:
            检索指标
        """
        relevant_set = set(relevant_docs)
        retrieved_set = set(retrieved_docs[:k])

        # Precision@K
        precision = len(relevant_set & retrieved_set) / k if k > 0 else 0

        # Recall@K
        recall = len(relevant_set & retrieved_set) / len(relevant_set) if len(relevant_set) > 0 else 0

        # F1 Score
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0

        # Mean Reciprocal Rank (MRR)
        mrr = 0
        for i, doc in enumerate(retrieved_docs[:k], 1):
            if doc in relevant_set:
                mrr = 1 / i
                break

        # NDCG@K
        dcg = 0
        for i, doc in enumerate(retrieved_docs[:k], 1):
            if doc in relevant_set:
                dcg += 1 / np.log2(i + 1)

        # Ideal DCG
        idcg = sum(1 / np.log2(i + 1) for i in range(1, min(k, len(relevant_docs)) + 1))
        ndcg = dcg / idcg if idcg > 0 else 0

        return RetrievalMetrics(
            precision=precision,
            recall=recall,
            f1=f1,
            mrr=mrr,
            ndcg=ndcg,
        )

    def evaluate_generation(
        self,
        answer: str,
        reference_answer: Optional[str] = None,
        question: Optional[str] = None,
    ) -> GenerationMetrics:
        """
        评估生成质量（简化版本）

        Args:
            answer: 生成的答案
            reference_answer: 参考答案（可选）
            question: 问题（可选）

        Returns:
            生成指标
        """
        # 这里是简化版本，实际应该使用更复杂的评估方法
        # 例如：使用 LLM 评估、BLEU、ROUGE 等

        metrics = {
            "answer_length": len(answer),
            "has_reference": reference_answer is not None,
        }

        # 简单的相关性评估（基于关键词重叠）
        if question and reference_answer:
            question_words = set(question.lower().split())
            answer_words = set(answer.lower().split())

            relevance = len(question_words & answer_words) / len(question_words) if question_words else 0

            # 简单的准确性评估（基于参考答案）
            ref_words = set(reference_answer.lower().split())
            accuracy = len(ref_words & answer_words) / len(ref_words) if ref_words else 0

            # 完整性（答案长度）
            completeness = min(len(answer) / len(reference_answer), 1.0) if reference_answer else 0.5

        else:
            # 无参考答案时使用启发式评估
            relevance = 0.7  # 默认值
            accuracy = 0.7  # 默认值
            completeness = 0.7 if len(answer) > 50 else 0.5

        # 流利度（基于句子数量）
        sentence_count = answer.count('。') + answer.count('.') + answer.count('!')
        fluency = min(sentence_count / 3, 1.0) if sentence_count > 0 else 0.5

        return GenerationMetrics(
            relevance=relevance,
            accuracy=accuracy,
            completeness=completeness,
            fluency=fluency,
        )

    def evaluate_rag(
        self,
        question: str,
        answer: str,
        retrieved_docs: List[str],
        relevant_docs: Optional[List[str]] = None,
        reference_answer: Optional[str] = None,
        k: int = 5,
    ) -> Dict[str, Any]:
        """
        完整的 RAG 评估

        Args:
            question: 问题
            answer: 生成的答案
            retrieved_docs: 检索到的文档
            relevant_docs: 相关文档（可选）
            reference_answer: 参考答案（可选）
            k: 考虑的前 k 个结果

        Returns:
            评估结果
        """
        # 评估检索
        if relevant_docs:
            retrieval_metrics = self.evaluate_retrieval(
                retrieved_docs=retrieved_docs,
                relevant_docs=relevant_docs,
                k=k,
            )
        else:
            # 无标签时使用默认值
            retrieval_metrics = RetrievalMetrics(
                precision=0.7,
                recall=0.7,
                f1=0.7,
                mrr=0.7,
                ndcg=0.7,
            )

        # 评估生成
        generation_metrics = self.evaluate_generation(
            answer=answer,
            reference_answer=reference_answer,
            question=question,
        )

        # 综合得分
        retrieval_score = (
            retrieval_metrics.precision +
            retrieval_metrics.recall +
            retrieval_metrics.ndcg
        ) / 3

        generation_score = (
            generation_metrics.relevance +
            generation_metrics.accuracy +
            generation_metrics.completeness +
            generation_metrics.fluency
        ) / 4

        overall_score = (retrieval_score * 0.4) + (generation_score * 0.6)

        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "retrieval_metrics": {
                "precision": retrieval_metrics.precision,
                "recall": retrieval_metrics.recall,
                "f1": retrieval_metrics.f1,
                "mrr": retrieval_metrics.mrr,
                "ndcg": retrieval_metrics.ndcg,
                "score": retrieval_score,
            },
            "generation_metrics": {
                "relevance": generation_metrics.relevance,
                "accuracy": generation_metrics.accuracy,
                "completeness": generation_metrics.completeness,
                "fluency": generation_metrics.fluency,
                "score": generation_score,
            },
            "overall_score": overall_score,
        }

        self.evaluations.append(evaluation)
        logger.info(f"完成 RAG 评估: {overall_score:.3f}")

        return evaluation

    def get_average_scores(self, recent_n: Optional[int] = None) -> Dict[str, float]:
        """
        获取平均得分

        Args:
            recent_n: 只考虑最近的 n 次评估

        Returns:
            平均得分
        """
        evaluations = self.evaluations[-recent_n:] if recent_n else self.evaluations

        if not evaluations:
            return {
                "retrieval_score": 0,
                "generation_score": 0,
                "overall_score": 0,
            }

        retrieval_scores = [e["retrieval_metrics"]["score"] for e in evaluations]
        generation_scores = [e["generation_metrics"]["score"] for e in evaluations]
        overall_scores = [e["overall_score"] for e in evaluations]

        return {
            "retrieval_score": np.mean(retrieval_scores),
            "generation_score": np.mean(generation_scores),
            "overall_score": np.mean(overall_scores),
            "count": len(evaluations),
        }

    def export_evaluations(self, filepath: str) -> None:
        """
        导出评估结果

        Args:
            filepath: 文件路径
        """
        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.evaluations, f, ensure_ascii=False, indent=2)

        logger.info(f"导出 {len(self.evaluations)} 条评估记录到 {filepath}")


# 全局评估器实例
_evaluator = None


def get_rag_evaluator() -> RAGEvaluator:
    """获取 RAG 评估器（单例）"""
    global _evaluator
    if _evaluator is None:
        _evaluator = RAGEvaluator()
    return _evaluator
