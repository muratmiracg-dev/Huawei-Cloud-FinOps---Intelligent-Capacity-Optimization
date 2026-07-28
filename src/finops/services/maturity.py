"""Evidence-based FinOps maturity scoring."""

from __future__ import annotations

from collections.abc import Sequence

from finops.models import Recommendation


def calculate_maturity_score(
    *,
    allocation_coverage_pct: float,
    budget_coverage_pct: float,
    recommendations: Sequence[Recommendation],
    anomaly_count: int,
    automation_enabled: bool = True,
) -> float:
    visibility = min(100.0, allocation_coverage_pct)
    governance = min(100.0, budget_coverage_pct)
    optimization = 100.0 if recommendations else 55.0
    anomaly_readiness = 90.0 if anomaly_count >= 0 else 0.0
    automation = 90.0 if automation_enabled else 40.0
    score = (
        visibility * 0.25
        + governance * 0.25
        + optimization * 0.2
        + anomaly_readiness * 0.15
        + automation * 0.15
    )
    return round(score, 1)
