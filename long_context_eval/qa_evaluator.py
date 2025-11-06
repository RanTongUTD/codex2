"""Evaluation utilities for long-context question answering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .data_models import Document, Question
from .retrieval import make_context


@dataclass
class EvaluationResult:
    """Stores aggregate evaluation statistics."""

    num_questions: int
    exact_match: float
    f1: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "num_questions": float(self.num_questions),
            "exact_match": self.exact_match,
            "f1": self.f1,
        }


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def exact_match_score(prediction: str, reference: str) -> float:
    return 1.0 if _normalize_text(prediction) == _normalize_text(reference) else 0.0


def f1_score(prediction: str, reference: str) -> float:
    pred_tokens = _normalize_text(prediction).split()
    ref_tokens = _normalize_text(reference).split()
    if not pred_tokens and not ref_tokens:
        return 1.0
    if not pred_tokens or not ref_tokens:
        return 0.0
    common = 0
    ref_counts: Dict[str, int] = {}
    for token in ref_tokens:
        ref_counts[token] = ref_counts.get(token, 0) + 1
    for token in pred_tokens:
        if ref_counts.get(token, 0) > 0:
            common += 1
            ref_counts[token] -= 1
    if common == 0:
        return 0.0
    precision = common / len(pred_tokens)
    recall = common / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)


def naive_answer(document: Document, question: Question) -> str:
    """Return a naive answer by selecting the first retrieved sentence."""

    context = make_context(document, question, max_sentences=3)
    return context.split("\n")[0] if context else ""


def evaluate_dataset(
    dataset,
    answer_fn=naive_answer,
) -> EvaluationResult:
    """Evaluate a dataset using the provided answering function."""

    total_em = 0.0
    total_f1 = 0.0
    num_questions = 0
    for document, question in dataset.iter_questions():
        prediction = answer_fn(document, question)
        reference = question.answer.text
        total_em += exact_match_score(prediction, reference)
        total_f1 += f1_score(prediction, reference)
        num_questions += 1
    if num_questions == 0:
        return EvaluationResult(num_questions=0, exact_match=0.0, f1=0.0)
    return EvaluationResult(
        num_questions=num_questions,
        exact_match=total_em / num_questions,
        f1=total_f1 / num_questions,
    )
