"""CSV adapter for Huawei Cost Center exports and the deterministic demo data."""

from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

from finops.models import (
    Budget,
    CloudResource,
    CostRecord,
    PricingMode,
    ServiceType,
    UtilizationSample,
)


def _bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise ValueError(
        "Invalid boolean value for attached: "
        f"{value!r}; expected true/false, yes/no, y/n, or 1/0"
    )


class CsvRepository:
    """Load the canonical local contract from four CSV files."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def _rows(self, filename: str) -> list[dict[str, str]]:
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required data file not found: {path}")
        with path.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def resources(self) -> list[CloudResource]:
        records: list[CloudResource] = []
        for row in self._rows("resources.csv"):
            records.append(
                CloudResource(
                    resource_id=row["resource_id"],
                    name=row["name"],
                    service=ServiceType(row["service"]),
                    region=row["region"],
                    enterprise_project=row["enterprise_project"],
                    environment=row["environment"],
                    owner=row["owner"],
                    cost_center=row["cost_center"],
                    product=row["product"],
                    monthly_cost=float(row["monthly_cost"]),
                    pricing_mode=PricingMode(row["pricing_mode"]),
                    vcpu=int(row["vcpu"] or 0),
                    memory_gb=float(row["memory_gb"] or 0),
                    storage_gb=float(row["storage_gb"] or 0),
                    status=row["status"],
                    attached=_bool(row["attached"]),
                    schedule=row["schedule"],
                    criticality=row["criticality"],
                    tags=json.loads(row["tags_json"] or "{}"),
                )
            )
        return records

    def costs(self) -> list[CostRecord]:
        return [
            CostRecord(
                record_date=date.fromisoformat(row["date"]),
                resource_id=row["resource_id"],
                service=ServiceType(row["service"]),
                actual_cost=float(row["actual_cost"]),
                amortized_cost=float(row["amortized_cost"]),
                usage_quantity=float(row["usage_quantity"]),
                currency=row["currency"],
            )
            for row in self._rows("costs.csv")
        ]

    def utilization(self) -> list[UtilizationSample]:
        return [
            UtilizationSample(
                timestamp=datetime.fromisoformat(row["timestamp"]),
                resource_id=row["resource_id"],
                cpu_pct=float(row["cpu_pct"]),
                memory_pct=float(row["memory_pct"]),
                network_pct=float(row["network_pct"]),
                disk_pct=float(row["disk_pct"]),
                request_cpu_pct=float(row["request_cpu_pct"]),
                request_memory_pct=float(row["request_memory_pct"]),
            )
            for row in self._rows("utilization.csv")
        ]

    def budgets(self) -> list[Budget]:
        return [
            Budget(
                name=row["name"],
                scope_type=row["scope_type"],
                scope_value=row["scope_value"],
                monthly_limit=float(row["monthly_limit"]),
                actual_alert_pct=float(row["actual_alert_pct"]),
                forecast_alert_pct=float(row["forecast_alert_pct"]),
                currency=row["currency"],
            )
            for row in self._rows("budgets.csv")
        ]
