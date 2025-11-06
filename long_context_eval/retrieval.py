"""Simple keyword-based retrieval for long documents."""

from __future__ import annotations

from collections import Counter
from math import sqrt
from typing import List, Sequence

from .data_models import Document, Question


def tokenize(text: str) -> List[str]:
    return [token.strip(".,;:!?()[]\"'").lower() for token in text.split() if token]


def vectorize(tokens: Sequence[str]) -> Counter[str]:
    return Counter(token for token in tokens if token)


def cosine_similarity(vec_a: Counter[str], vec_b: Counter[str]) -> float:
    shared = set(vec_a) & set(vec_b)
    numerator = sum(vec_a[token] * vec_b[token] for token in shared)
    denominator = sqrt(sum(v * v for v in vec_a.values())) * sqrt(
        sum(v * v for v in vec_b.values())
    )
    if denominator == 0:
        return 0.0
    return numerator / denominator


def rank_sentences(document: Document, question: Question, top_k: int = 5) -> List[str]:
    """Return the most relevant sentences for a question."""

    question_vec = vectorize(question.keywords())
    scored: List[tuple[float, str]] = []
    for sentence in document.sentences():
        sentence_vec = vectorize(tokenize(sentence))
        score = cosine_similarity(question_vec, sentence_vec)
        if score > 0:
            scored.append((score, sentence))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [sentence for _, sentence in scored[:top_k]]


def make_context(document: Document, question: Question, max_sentences: int = 5) -> str:
    """Assemble a compact context string from the top-ranked sentences."""

    sentences = rank_sentences(document, question, top_k=max_sentences)
    if sentences:
        return " \n".join(sentences)
    # fallback to the first portion of the document if retrieval fails
    return " ".join(list(document.sentences())[:max_sentences])
