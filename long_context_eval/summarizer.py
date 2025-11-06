"""Lightweight summarization utilities for long documents."""

from __future__ import annotations

from collections import Counter
from typing import List

from .data_models import Document
from .retrieval import tokenize


def sentence_importance(sentence: str, global_counts: Counter[str]) -> float:
    """Compute sentence importance using term frequency weighting."""

    tokens = tokenize(sentence)
    if not tokens:
        return 0.0
    token_counts = Counter(tokens)
    importance = 0.0
    for token, count in token_counts.items():
        importance += count * global_counts[token]
    return importance / len(tokens)


def summarize(document: Document, max_sentences: int = 5) -> List[str]:
    """Return the top sentences as a simple extractive summary."""

    sentences = list(document.sentences())
    global_counts = Counter(token for sentence in sentences for token in tokenize(sentence))
    scored = [
        (sentence_importance(sentence, global_counts), idx, sentence)
        for idx, sentence in enumerate(sentences)
    ]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [sentence for _, _, sentence in scored[:max_sentences]]


def make_summary_text(document: Document, max_sentences: int = 5) -> str:
    """Return a formatted summary string."""

    return " \n".join(summarize(document, max_sentences=max_sentences))
