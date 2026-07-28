from __future__ import annotations

import json
from pathlib import Path

import pytest

from finops.cli import build_parser, main

DEMO_DIR = Path(__file__).resolve().parents[1] / "data/demo"


def test_summary_command_prints_executive_kpis(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--data-dir", str(DEMO_DIR), "summary"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["current_monthly_cost"] == 6_133.36
    assert payload["estimated_monthly_savings"] == 1_520.7


def test_recommendations_command_prints_prioritized_actions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--data-dir", str(DEMO_DIR), "recommendations"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 21
    assert payload[0]["risk"] in {"high", "medium", "low"}


def test_analyze_command_writes_reproducible_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "nested" / "analysis.json"

    result = main(
        [
            "--data-dir",
            str(DEMO_DIR),
            "analyze",
            "--forecast-months",
            "2",
            "--output",
            str(output),
        ]
    )

    assert result == 0
    assert f"Analysis written to {output}" in capsys.readouterr().out
    payload = json.loads(output.read_text())
    assert len(payload["forecast"]) == 2
    assert set(payload["allocation"]) == {
        "service",
        "enterprise_project",
        "environment",
        "cost_center",
        "product",
    }


def test_parser_requires_subcommand() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
