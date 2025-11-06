# Long Context Evaluation Toolkit

This repository provides a lightweight, fully offline toolkit for exploring long-context
question answering failures and baseline mitigations. It offers:

- A JSON dataset format for pairing long-form documents (2014–2025) with evaluation questions.
- Keyword-based retrieval to construct compact contexts from long documents.
- A naive question answering baseline with exact match and token-level F1 scoring.
- Extractive summarization utilities to compress long documents before querying.
- A command-line interface for dataset inspection, evaluation, and summary export.

## Getting Started

Create a virtual environment and install the project in editable mode (optional):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The toolkit has no third-party dependencies and runs on standard Python 3.11 installations.

### Sample Dataset

A small synthetic dataset derived from 2024–2025 reports is provided at
`data/sample_dataset.json`. Each entry contains document metadata, full text, and
multi-category question annotations.

### CLI Usage

Run the built-in CLI with Python’s module runner:

```bash
python -m long_context_eval.cli summary data/sample_dataset.json
```

```
python -m long_context_eval.cli evaluate data/sample_dataset.json
```

```
python -m long_context_eval.cli export-summaries data/sample_dataset.json --sentences 4
```

The `summary` command prints corpus-level statistics, `evaluate` runs the naive QA baseline,
and `export-summaries` produces extractive summaries for downstream experiments.

### Programmatic API

```python
from long_context_eval import LongContextDataset, evaluate_dataset

dataset = LongContextDataset.from_json("data/sample_dataset.json")
result = evaluate_dataset(dataset)
print(result.as_dict())
```

Use the exposed utilities as building blocks for retrieval-augmented or fine-tuned models that
tackle long-context reasoning challenges.
