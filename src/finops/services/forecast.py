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
    history = with_run_rate(monthly_costs(records), month_completion_ratio(records))
    history = with_start_run_rate(history, first_month_completion_ratio(records))
    return forecast_monthly_series(history, months)


def forecast_monthly_series(
    history: Sequence[tuple[str, float]], months: int = 3
) -> list[ForecastPoint]:
    """Forecast from ``(YYYY-MM, cost)`` pairs in ascending period order."""

    if type(months) is not int:
        raise TypeError("months must be an integer")
    if months < 1 or months > 18:
        raise ValueError("months must be between 1 and 18")
    if not history:
        return []
    values = [value for _, value in history]
    periods = [date.fromisoformat(f"{period}-01") for period, _ in history]
    origin = periods[0].year * 12 + periods[0].month - 1
    x_values = [period.year * 12 + period.month - 1 - origin for period in periods]
    if len(values) == 1:
        intercept, slope = values[0], 0.0
        residual_stddev = values[0] * 0.1
    else:
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

    latest = periods[-1]
    output: list[ForecastPoint] = []
    for offset in range(1, months + 1):
        target_year, target_month = _next_month(latest.year, latest.month, offset)
        x_value = x_values[-1] + offset
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
    """Share of the latest billing month covered by the data, in (0, 1].

    Daily billing exports usually end part-way through the current month. A month
    counts as partial only when the data is evidently daily: the previous month's
    records run to its last calendar day while the latest month's stop earlier.
    Monthly exports (one record per month, often dated the 1st) and single-month
    histories are treated as complete, because day-of-month says nothing there.
    """

    if not records:
        return 1.0
    dates = {record.record_date for record in records}
    latest = max(dates)
    previous_year, previous_month = _next_month(latest.year, latest.month, -1)
    previous = [
        d for d in dates if (d.year, d.month) == (previous_year, previous_month)
    ]
    if not previous:
        return 1.0
    if max(previous).day != calendar.monthrange(previous_year, previous_month)[1]:
        return 1.0
    days_in_month = calendar.monthrange(latest.year, latest.month)[1]
    return min(1.0, latest.day / days_in_month)


def first_month_completion_ratio(records: Sequence[CostRecord]) -> float:
    """Share of the earliest billing month covered by the data, in (0, 1].

    The mirror image of ``month_completion_ratio``: a daily export that starts on
    15 March holds half of March, and reading it as a full month makes the first
    point look like a low and bends the trend upward. The month counts as partial only
    when the data is evidently daily: the following month's records start on its first
    day while the earliest month's start later.
    """

    if not records:
        return 1.0
    dates = {record.record_date for record in records}
    earliest = min(dates)
    if earliest.day == 1:
        return 1.0
    next_year, next_month = _next_month(earliest.year, earliest.month, 1)
    following = [d for d in dates if (d.year, d.month) == (next_year, next_month)]
    if not following or min(following).day != 1:
        return 1.0
    days_in_month = calendar.monthrange(earliest.year, earliest.month)[1]
    return (days_in_month - earliest.day + 1) / days_in_month


def with_start_run_rate(
    history: Sequence[tuple[str, float]], completion: float
) -> list[tuple[str, float]]:
    """Scale a partial earliest month to a full-month run rate (needs two or more months)."""

    adjusted = list(history)
    if len(adjusted) >= 2 and 0 < completion < 1:
        period, value = adjusted[0]
        adjusted[0] = (period, round(value / completion, 2))
    return adjusted


def with_run_rate(
    history: Sequence[tuple[str, float]], completion: float
) -> list[tuple[str, float]]:
    """Scale a partial latest month to a full-month run rate.

    Treating month-to-date spend as a full month makes the latest point look like a
    sharp drop, which bends the trend down and hides forecast budget breaches.
    """

    adjusted = list(history)
    if adjusted and 0 < completion < 1:
        period, value = adjusted[-1]
        adjusted[-1] = (period, round(value / completion, 2))
    return adjusted


def latest_month_run_rate(records: Sequence[CostRecord]) -> float:
    """Latest month's cost, projected to a full month when the month is partial."""

    history = with_run_rate(monthly_costs(records), month_completion_ratio(records))
    return history[-1][1] if history else 0.0
