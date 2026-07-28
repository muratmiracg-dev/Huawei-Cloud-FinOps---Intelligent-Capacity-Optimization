"""Robust cost anomaly detection using rolling median and MAD."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from finops.models import CostAnomaly, CostRecord, RiskLevel
from finops.services.statistics import median


def detect_cost_anomalies(
    records: Sequence[CostRecord],
    *,
    window: int = 14,
    minimum_history: int = 7,
    minimum_deviation_pct: float = 25.0,
) -> list[CostAnomaly]:
    daily: defaultdict[str, defaultdict[object, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    for record in records:
        daily[record.resource_id][record.record_date] += record.amortized_cost

    anomalies: list[CostAnomaly] = []
    for resource_id, points in daily.items():
        ordered = sorted(points.items())
        for index, (record_date, actual) in enumerate(ordered):
            history = [value for _, value in ordered[max(0, index - window) : index]]
            if len(history) < minimum_history:
                continue
            expected = median(history)
            deviations = [abs(value - expected) for value in history]
            mad = median(deviations)
            robust_scale = max(1.4826 * mad, expected * 0.05, 0.01)
            score = (actual - expected) / robust_scale
            deviation_pct = (
                (actual - expected) / expected * 100 if expected > 0 else 0.0
            )
            if score < 3.5 or deviation_pct < minimum_deviation_pct:
                continue
            severity = (
                RiskLevel.CRITICAL
                if deviation_pct >= 100
                else RiskLevel.HIGH
                if deviation_pct >= 60
                else RiskLevel.MEDIUM
            )
            anomalies.append(
                CostAnomaly(
                    resource_id=resource_id,
                    anomaly_date=record_date,
                    actual_cost=round(actual, 2),
                    expected_cost=round(expected, 2),
                    deviation_pct=round(deviation_pct, 2),
                    score=round(score, 2),
                    severity=severity,
                )
            )
    return sorted(
        anomalies,
        key=lambda item: (item.anomaly_date, item.score),
        reverse=True,
    )
