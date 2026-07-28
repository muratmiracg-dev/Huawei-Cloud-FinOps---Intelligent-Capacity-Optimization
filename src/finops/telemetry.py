"""Prometheus exposition with a dependency-free fallback."""

from __future__ import annotations

from finops.models import FinOpsSummary


def render_metrics(summary: FinOpsSummary) -> str:
    metrics = {
        "finops_current_monthly_cost": summary.current_monthly_cost,
        "finops_estimated_monthly_savings": summary.estimated_monthly_savings,
        "finops_savings_opportunity_ratio": summary.savings_opportunity_pct / 100,
        "finops_allocation_coverage_ratio": summary.allocation_coverage_pct / 100,
        "finops_budget_coverage_ratio": summary.budget_coverage_pct / 100,
        "finops_recommendations_total": summary.recommendation_count,
        "finops_high_risk_recommendations_total": summary.high_risk_count,
        "finops_cost_anomalies_total": summary.anomaly_count,
        "finops_maturity_score": summary.maturity_score,
    }
    lines: list[str] = []
    for name, value in metrics.items():
        lines.extend(
            [
                f"# TYPE {name} gauge",
                f"{name} {value}",
            ]
        )
    return "\n".join(lines) + "\n"
