#!/usr/bin/env python3
"""Run end-to-end smoke tests for the long-context evaluation CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def run_cli(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    """Execute the CLI with the provided arguments and return the process result."""
    command = [sys.executable, "-m", "long_context_eval.cli", *arguments]
    print(f"\n$ {' '.join(command)}")
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    if completed.stdout:
        print(completed.stdout.strip())
    if completed.stderr:
        print(completed.stderr.strip(), file=sys.stderr)
    return completed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the CLI smoke-test sequence and validate its outputs.",
    )
    parser.add_argument(
        "--dataset",
        default="data/sample_dataset.json",
        type=Path,
        help="Path to the dataset JSON file (defaults to the bundled sample dataset).",
    )
    parser.add_argument(
        "--sentences",
        default=4,
        type=int,
        help="Number of sentences per summary for the export-summaries command.",
    )
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Persist the generated summaries.json file instead of cleaning it up.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Explicit path for the exported summaries file (defaults to a temp file).",
    )
    args = parser.parse_args()

    dataset_path = args.dataset.resolve()
    if not dataset_path.exists():
        raise SystemExit(f"Dataset not found: {dataset_path}")
    print(f"Using dataset: {dataset_path}")

    run_cli(["summary", str(dataset_path)])
    run_cli(["evaluate", str(dataset_path)])

    tmp_dir: TemporaryDirectory[str] | None = None
    if args.output is not None:
        summaries_path = args.output.resolve()
        summaries_path.parent.mkdir(parents=True, exist_ok=True)
        cleanup_required = False
    else:
        tmp_dir = TemporaryDirectory()
        summaries_path = Path(tmp_dir.name) / "summaries.json"
        cleanup_required = True

    try:
        run_cli(
            [
                "export-summaries",
                str(dataset_path),
                "--sentences",
                str(args.sentences),
                "--output",
                str(summaries_path),
            ]
        )
        summaries = json.loads(summaries_path.read_text())
        if not summaries:
            raise RuntimeError("The summaries file is empty; expected one entry per document.")
        print(f"Validated {len(summaries)} summaries at {summaries_path}")
    finally:
        if cleanup_required:
            if args.keep_output:
                destination = Path.cwd() / "summaries.smoke.json"
                shutil.copyfile(summaries_path, destination)
                print(f"Summaries file copied to {destination}")
            else:
                summaries_path.unlink(missing_ok=True)
            if tmp_dir is not None:
                tmp_dir.cleanup()
        elif args.keep_output:
            print(f"Summaries file retained at {summaries_path}")


if __name__ == "__main__":
    main()
