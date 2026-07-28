"""Huawei Cloud billing export normalization.

This adapter intentionally accepts exported records instead of embedding
credentials. Production collectors can stream Cost Details Export objects from
OBS or map Billing Center API responses into the same canonical contract.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

from finops.models import CostRecord, ServiceType

SERVICE_ALIASES = {
    "Elastic Cloud Server": ServiceType.ECS,
    "Cloud Container Engine": ServiceType.CCE_NODE,
    "Elastic Volume Service": ServiceType.EVS,
    "Elastic IP": ServiceType.EIP,
    "Relational Database Service": ServiceType.RDS,
    "Object Storage Service": ServiceType.OBS,
    "Elastic Load Balance": ServiceType.ELB,
}


def normalize_billing_records(rows: Iterable[dict[str, Any]]) -> list[CostRecord]:
    """Normalize selected Cost Center/Billing Center fields.

    Field aliases cover common English export headers. Keeping this pure makes
    the mapping independently testable and safe for offline portfolio demos.
    """

    records: list[CostRecord] = []
    for row in rows:
        service_name = str(row.get("Service Type") or row.get("service_type") or "")
        service = SERVICE_ALIASES.get(service_name, ServiceType.OTHER)
        raw_date = str(row.get("Usage Date") or row.get("date"))
        actual = float(row.get("Net Amount") or row.get("actual_cost") or 0.0)
        amortized = float(
            row.get("Amortized Net Amount") or row.get("amortized_cost") or actual
        )
        records.append(
            CostRecord(
                record_date=date.fromisoformat(raw_date[:10]),
                resource_id=str(
                    row.get("Resource ID") or row.get("resource_id") or "unallocated"
                ),
                service=service,
                actual_cost=actual,
                amortized_cost=amortized,
                usage_quantity=float(
                    row.get("Usage") or row.get("usage_quantity") or 0.0
                ),
                currency=str(row.get("Currency") or row.get("currency") or "USD"),
            )
        )
    return records
