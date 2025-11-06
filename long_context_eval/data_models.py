"""Core data models used in the long-context evaluation toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence


@dataclass
class Answer:
    """Stores a ground-truth answer and optional supporting span."""

    text: str
    supporting_span: str | None = None

    def normalize(self) -> str:
        """Return a normalized version of the answer for comparisons."""

        return " ".join(self.text.lower().split())


@dataclass
class Question:
    """Represents a single question about a document."""

    id: str
    text: str
    answer: Answer
    category: str = "factual"

    def keywords(self) -> List[str]:
        """Extract a list of lowercase keywords from the question."""

        tokens = [token.strip(".,;:!?()[]\"'") for token in self.text.lower().split()]
        return [token for token in tokens if token and token not in _STOP_WORDS]


@dataclass
class Document:
    """Represents a long-form document paired with questions."""

    id: str
    title: str
    text: str
    year: int
    questions: Sequence[Question] = field(default_factory=list)
    domain: str = "unknown"

    def sentences(self) -> Iterable[str]:
        """Yield sentences using a naive period-based splitter."""

        sentence = []
        for token in self.text.split():
            sentence.append(token)
            if token.endswith(('.', '?', '!')):
                yield " ".join(sentence).strip()
                sentence = []
        if sentence:
            yield " ".join(sentence).strip()


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
}
