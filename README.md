# Long Context Evaluation Toolkit

This repository provides a lightweight, fully offline toolkit for exploring long-context
question answering failures and baseline mitigations. It offers:

- A JSON dataset format for pairing long-form documents (2014–2025) with evaluation questions.
- Keyword-based retrieval to construct compact contexts from long documents.
- A naive question answering baseline with exact match and token-level F1 scoring.
- Extractive summarization utilities to compress long documents before querying.
- A command-line interface for dataset inspection, evaluation, and summary export.

## Completed Tasks

The current release of the toolkit includes the following delivered tasks:

- Implemented the `long_context_eval` Python package with dataset loading, retrieval,
  summarization, and baseline QA evaluation modules.
- Curated a synthetic 2024–2025 sample dataset (`data/sample_dataset.json`) for immediate
  experimentation and testing.
- Built a CLI (`long_context_eval.cli`) that surfaces dataset summaries, evaluation metrics,
  and extractive summaries through dedicated subcommands.
- Added an automated smoke-test helper script
  (`scripts/run_cli_smoke_tests.py`) to exercise the CLI end-to-end and validate outputs.

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

### Testing the Toolkit

To verify that everything works end-to-end, execute the three CLI commands above and
confirm they complete without raising errors. When run against the bundled sample dataset
you should observe:

1. **Dataset summary** output that includes document counts, year range, and token
   statistics.
2. **Evaluation** output with per-question predictions and aggregated Exact Match / F1
   metrics.
3. **Summary export** creation of a `summaries.json` file containing the requested number
   of sentences per document.

The commands can be chained in a shell session, for example:

```bash
python -m long_context_eval.cli summary data/sample_dataset.json \
  && python -m long_context_eval.cli evaluate data/sample_dataset.json \
  && python -m long_context_eval.cli export-summaries data/sample_dataset.json \
       --sentences 4 --output summaries.json
```

Inspect the generated `summaries.json` file to ensure it contains extractive summaries and
delete it when you are finished testing.

#### Automated smoke test script

If you prefer a single command, run the bundled smoke-test helper which wraps the three
CLI invocations and validates the generated summaries file:

```bash
python scripts/run_cli_smoke_tests.py
```

Pass `--keep-output` to preserve the generated summaries (they default to a temporary
location) or `--dataset` to point at a different JSON dataset when running your own
experiments.

### Running on Google Colab

If Colab is your primary environment, the entire toolkit can be exercised in a single
notebook cell. The snippet below clones the public repository, installs the package in
editable mode, and runs the smoke-test script while keeping the exported summaries for
inspection:

> **Important:** In Colab, put `%%bash` on the very first line of a new cell—do not
> prefix the snippet with `python` or run it inside a Python cell, otherwise you will
> see a `SyntaxError`.

```bash
%%bash
git clone https://github.com/RanTongUTD/codex2.git
cd codex2
pip install -e .
python scripts/run_cli_smoke_tests.py --keep-output --output /content/codex2_summaries.json
```

To stay inside pure Python (avoiding a `%%bash` cell), you can also paste the following
helper code which reproduces the same workflow via `subprocess` calls:

```python
import subprocess
import sys
from pathlib import Path

repo_dir = Path("/content/codex2")
if not repo_dir.exists():
    subprocess.run(["git", "clone", "https://github.com/RanTongUTD/codex2.git", str(repo_dir)], check=True)

subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(repo_dir)] , check=True)

smoke_test = repo_dir / "scripts" / "run_cli_smoke_tests.py"
subprocess.run([
    sys.executable,
    str(smoke_test),
    "--keep-output",
    "--output",
    "/content/codex2_summaries.json",
], check=True)
```

After either variant finishes, open `/content/codex2_summaries.json` in Colab to inspect the
generated summaries or adjust the script arguments (e.g., `--dataset`) to point at your own
long-context collections.

### Programmatic API

```python
from long_context_eval import LongContextDataset, evaluate_dataset

dataset = LongContextDataset.from_json("data/sample_dataset.json")
result = evaluate_dataset(dataset)
print(result.as_dict())
```

Use the exposed utilities as building blocks for retrieval-augmented or fine-tuned models that
tackle long-context reasoning challenges.
