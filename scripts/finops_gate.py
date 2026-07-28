#!/usr/bin/env python3
"""CI gate for cost, allocation, and capacity-risk thresholds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Evaluate a FinOps analysis artifact."
    )
    command.add_argument("analysis", type=Path)
    command.add_argument("--max-monthly-cost", type=float, required=True)
    command.add_argument("--min-allocation-coverage", type=float, default=95)
    command.add_argument("--max-high-risk", type=int, default=2)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    payload = json.loads(args.analysis.read_text(encoding="utf-8"))
    summary = payload["summary"]
    failures: list[str] = []
    if summary["current_monthly_cost"] > args.max_monthly_cost:
        failures.append(
            "monthly cost "
            f"{summary['current_monthly_cost']:.2f} exceeds "
            f"{args.max_monthly_cost:.2f}"
        )
    if summary["allocation_coverage_pct"] < args.min_allocation_coverage:
        failures.append(
            "allocation coverage "
            f"{summary['allocation_coverage_pct']:.2f}% is below "
            f"{args.min_allocation_coverage:.2f}%"
        )
    if summary["high_risk_count"] > args.max_high_risk:
        failures.append(
            f"{summary['high_risk_count']} high-risk recommendations exceed "
            f"the approved maximum of {args.max_high_risk}"
        )
    if failures:
        print("FinOps policy gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "FinOps policy gate passed: "
        f"cost={summary['current_monthly_cost']:.2f}, "
        f"allocation={summary['allocation_coverage_pct']:.2f}%, "
        f"high_risk={summary['high_risk_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
