"""Command-line entry point for reproducible offline analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from finops.adapters import CsvRepository
from finops.engine import FinOpsEngine
from finops.models import model_to_dict


def _serialize(value: object) -> object:
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return model_to_dict(value)
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="finops",
        description="Huawei Cloud FinOps and capacity optimization toolkit.",
    )
    parser.add_argument("--data-dir", default="data/demo")
    subcommands = parser.add_subparsers(dest="command", required=True)

    analyze = subcommands.add_parser("analyze", help="Run the full decision loop.")
    analyze.add_argument("--forecast-months", type=int, default=3)
    analyze.add_argument("--output", default="reports/demo-analysis.json")

    subcommands.add_parser("summary", help="Print the executive KPI summary.")
    subcommands.add_parser(
        "recommendations", help="Print prioritized optimization recommendations."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    engine = FinOpsEngine(CsvRepository(args.data_dir))
    if args.command == "summary":
        result = engine.summary()
    elif args.command == "recommendations":
        result = engine.recommendations()
    else:
        result = engine.full_analysis(args.forecast_months)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(_serialize(result), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Analysis written to {output}")
        return 0
    print(json.dumps(_serialize(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
