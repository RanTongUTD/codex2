"""Utilities for loading long-context evaluation datasets."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Iterator, List

from .data_models import Answer, Document, Question


@dataclass
class LongContextDataset:
    """Dataset consisting of multiple documents with questions."""

    documents: List[Document]

    @classmethod
    def from_json(cls, path: str | Path) -> "LongContextDataset":
        """Load a dataset from a JSON file."""

        data = json.loads(Path(path).read_text())
        documents: List[Document] = []
        for raw_doc in data.get("documents", []):
            questions = [
                Question(
                    id=raw_q["id"],
                    text=raw_q["question"],
                    answer=Answer(
                        text=raw_q["answer"],
                        supporting_span=raw_q.get("answer_span"),
                    ),
                    category=raw_q.get("category", "factual"),
                )
                for raw_q in raw_doc.get("questions", [])
            ]
            documents.append(
                Document(
                    id=raw_doc["id"],
                    title=raw_doc.get("title", raw_doc["id"]),
                    text=raw_doc["text"],
                    year=int(raw_doc.get("year", 0)),
                    questions=questions,
                    domain=raw_doc.get("domain", "unknown"),
                )
            )
        return cls(documents=documents)

    def iter_questions(self) -> Iterator[tuple[Document, Question]]:
        """Yield (document, question) pairs."""

        for document in self.documents:
            for question in document.questions:
                yield document, question

    def filter_by_year(self, start_year: int, end_year: int) -> "LongContextDataset":
        """Return a dataset restricted to documents within a year range."""

        filtered_docs = [
            doc
            for doc in self.documents
            if start_year <= doc.year <= end_year
        ]
        return LongContextDataset(documents=filtered_docs)

    def summary(self) -> dict:
        """Return basic summary statistics for the dataset."""

        domains: dict[str, int] = {}
        total_questions = 0
        for document in self.documents:
            total_questions += len(document.questions)
            domains[document.domain] = domains.get(document.domain, 0) + 1
        return {
            "num_documents": len(self.documents),
            "num_questions": total_questions,
            "domains": domains,
        }


def load_documents_from_directory(directory: str | Path) -> Iterable[Document]:
    """Load each JSON file in a directory as a document."""

    for path in Path(directory).glob("*.json"):
        dataset = LongContextDataset.from_json(path)
        for document in dataset.documents:
            yield document
