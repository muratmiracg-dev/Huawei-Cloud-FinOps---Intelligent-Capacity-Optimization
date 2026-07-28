"""Transparent monthly cost forecasting with trend and uncertainty bands."""

from __future__ import annotations

import calendar
from collections import defaultdict
from collections.abc import Sequence
from datetime import date

from finops.models import CostRecord, ForecastPoint
from finops.services.statistics import sample_stddev


def _next_month(year: int, month: int, offset: int) -> tuple[int, int]:
    zero_based = year * 12 + (month - 1) + offset
    return zero_based // 12, zero_based % 12 + 1


def monthly_costs(records: Sequence[CostRecord]) -> list[tuple[str, float]]:
    grouped: defaultdict[tuple[int, int], float] = defaultdict(float)
    for record in records:
        grouped[(record.record_date.year, record.record_date.month)] += (
            record.amortized_cost
        )
    return [
        (f"{year:04d}-{month:02d}", round(value, 2))
        for (year, month), value in sorted(grouped.items())
    ]


def forecast_monthly_cost(
    records: Sequence[CostRecord], months: int = 3
) -> list[ForecastPoint]:
    if months < 1 or months > 18:
        raise ValueError("months must be between 1 and 18")
    history = monthly_costs(records)
    if not history:
        return []
    values = [value for _, value in history]
    if len(values) == 1:
        intercept, slope = values[0], 0.0
        residual_stddev = values[0] * 0.1
    else:
        x_values = list(range(len(values)))
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(values) / len(values)
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        slope = (
            sum(
                (x - x_mean) * (y - y_mean)
                for x, y in zip(x_values, values, strict=True)
            )
            / denominator
            if denominator
            else 0.0
        )
        intercept = y_mean - slope * x_mean
        fitted = [intercept + slope * x for x in x_values]
        residual_stddev = sample_stddev(
            [actual - estimate for actual, estimate in zip(values, fitted, strict=True)]
        )
        residual_stddev = max(residual_stddev, y_mean * 0.03)

    latest = date.fromisoformat(f"{history[-1][0]}-01")
    output: list[ForecastPoint] = []
    for offset in range(1, months + 1):
        target_year, target_month = _next_month(latest.year, latest.month, offset)
        x_value = len(values) - 1 + offset
        prediction = max(0.0, intercept + slope * x_value)
        uncertainty = 1.64 * residual_stddev * (offset**0.5)
        output.append(
            ForecastPoint(
                period=f"{target_year:04d}-{target_month:02d}",
                predicted_cost=round(prediction, 2),
                lower_bound=round(max(0.0, prediction - uncertainty), 2),
                upper_bound=round(prediction + uncertainty, 2),
            )
        )
    return output


def latest_month_cost(records: Sequence[CostRecord]) -> float:
    history = monthly_costs(records)
    return history[-1][1] if history else 0.0


def month_completion_ratio(records: Sequence[CostRecord]) -> float:
    if not records:
        return 1.0
    latest_date = max(record.record_date for record in records)
    days_in_month = calendar.monthrange(latest_date.year, latest_date.month)[1]
    return min(1.0, latest_date.day / days_in_month)
