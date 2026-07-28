"""Cost allocation and tag-governance analytics."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from finops.models import CloudResource

SUPPORTED_DIMENSIONS = {
    "service",
    "region",
    "enterprise_project",
    "environment",
    "owner",
    "cost_center",
    "product",
}


def allocation_by(
    resources: Sequence[CloudResource], dimension: str
) -> dict[str, float]:
    if dimension not in SUPPORTED_DIMENSIONS:
        choices = ", ".join(sorted(SUPPORTED_DIMENSIONS))
        raise ValueError(
            f"Unsupported allocation dimension '{dimension}'. Use: {choices}"
        )
    allocated: defaultdict[str, float] = defaultdict(float)
    for resource in resources:
        value = getattr(resource, dimension)
        if hasattr(value, "value"):
            value = value.value
        key = str(value).strip() or "unallocated"
        allocated[key] += resource.monthly_cost
    return dict(sorted(allocated.items(), key=lambda item: item[1], reverse=True))


def allocation_coverage(resources: Sequence[CloudResource]) -> float:
    total_cost = sum(resource.monthly_cost for resource in resources)
    if total_cost <= 0:
        return 100.0
    allocated_cost = sum(
        resource.monthly_cost
        for resource in resources
        if resource.cost_center.strip()
        and resource.owner.strip()
        and resource.product.strip()
        and resource.environment.strip()
    )
    return round(allocated_cost / total_cost * 100, 2)


def tag_compliance(resource: CloudResource) -> tuple[bool, list[str]]:
    required = {
        "owner": resource.owner,
        "cost-center": resource.cost_center,
        "environment": resource.environment,
        "product": resource.product,
    }
    missing = [
        key
        for key, canonical_value in required.items()
        if not canonical_value.strip() and not resource.tags.get(key, "").strip()
    ]
    return not missing, missing
