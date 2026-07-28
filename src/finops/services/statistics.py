"""Small dependency-free statistical helpers."""

from __future__ import annotations

import math
from collections.abc import Sequence


def percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = max(0.0, min(1.0, quantile)) * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def median(values: Sequence[float]) -> float:
    return percentile(values, 0.5)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def sample_stddev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))
