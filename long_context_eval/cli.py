"""Command-line interface for the long-context evaluation toolkit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset_loader import LongContextDataset
from .qa_evaluator import evaluate_dataset
from .summarizer import make_summary_text


def _cmd_summary(args: argparse.Namespace) -> None:
    dataset = LongContextDataset.from_json(args.dataset)
    if args.start_year or args.end_year:
        dataset = dataset.filter_by_year(args.start_year, args.end_year)
    summary = dataset.summary()
    print(json.dumps(summary, indent=2))


def _cmd_evaluate(args: argparse.Namespace) -> None:
    dataset = LongContextDataset.from_json(args.dataset)
    result = evaluate_dataset(dataset)
    print(json.dumps(result.as_dict(), indent=2))


def _cmd_export_summary(args: argparse.Namespace) -> None:
    dataset = LongContextDataset.from_json(args.dataset)
    summaries: dict[str, str] = {}
    for document in dataset.documents:
        summaries[document.id] = make_summary_text(document, max_sentences=args.sentences)
    Path(args.output).write_text(json.dumps(summaries, indent=2))
    print(f"Wrote summaries for {len(summaries)} documents to {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Utilities for evaluating long-context QA datasets",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser(
        "summary", help="Print dataset statistics",
    )
    summary_parser.add_argument("dataset", help="Path to the dataset JSON file")
    summary_parser.add_argument("--start-year", type=int, default=2014)
    summary_parser.add_argument("--end-year", type=int, default=2025)
    summary_parser.set_defaults(func=_cmd_summary)

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate the baseline QA system",
    )
    evaluate_parser.add_argument("dataset", help="Path to the dataset JSON file")
    evaluate_parser.set_defaults(func=_cmd_evaluate)

    export_parser = subparsers.add_parser(
        "export-summaries", help="Write extractive summaries to disk",
    )
    export_parser.add_argument("dataset", help="Path to the dataset JSON file")
    export_parser.add_argument(
        "--sentences",
        type=int,
        default=5,
        help="Number of sentences per summary",
    )
    export_parser.add_argument(
        "--output",
        type=str,
        default="summaries.json",
        help="Output path for the summaries JSON file",
    )
    export_parser.set_defaults(func=_cmd_export_summary)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
