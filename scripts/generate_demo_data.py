#!/usr/bin/env python3
"""Generate a deterministic, non-sensitive Huawei Cloud-shaped demo dataset."""

from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

SEED = 20260728
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 6, 30)

RESOURCES = [
    {
        "resource_id": "ecs-prod-web-01",
        "name": "commerce-web-prod-01",
        "service": "ECS",
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "production",
        "owner": "platform-team",
        "cost_center": "CC-100",
        "product": "Commerce",
        "monthly_cost": 620,
        "pricing_mode": "pay_per_use",
        "vcpu": 8,
        "memory_gb": 32,
        "storage_gb": 160,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "high",
        "tags": {"managed-by": "terraform"},
        "profile": (52, 59, 32, 68, 72),
    },
    {
        "resource_id": "ecs-prod-web-02",
        "name": "commerce-web-prod-02",
        "service": "ECS",
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "production",
        "owner": "platform-team",
        "cost_center": "CC-100",
        "product": "Commerce",
        "monthly_cost": 510,
        "pricing_mode": "yearly_monthly",
        "vcpu": 8,
        "memory_gb": 32,
        "storage_gb": 120,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "high",
        "tags": {"managed-by": "terraform"},
        "profile": (19, 28, 17, 55, 62),
    },
    {
        "resource_id": "cce-prod-node-a",
        "name": "cce-commerce-prod-a",
        "service": "CCE_NODE",
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "production",
        "owner": "sre-team",
        "cost_center": "CC-100",
        "product": "Commerce",
        "monthly_cost": 740,
        "pricing_mode": "yearly_monthly",
        "vcpu": 16,
        "memory_gb": 64,
        "storage_gb": 200,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "high",
        "tags": {"cluster": "commerce-prod"},
        "profile": (24, 34, 18, 70, 72),
    },
    {
        "resource_id": "cce-prod-node-b",
        "name": "cce-commerce-prod-b",
        "service": "CCE_NODE",
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "production",
        "owner": "sre-team",
        "cost_center": "CC-100",
        "product": "Commerce",
        "monthly_cost": 740,
        "pricing_mode": "yearly_monthly",
        "vcpu": 16,
        "memory_gb": 64,
        "storage_gb": 200,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "high",
        "tags": {"cluster": "commerce-prod"},
        "profile": (82, 86, 55, 90, 91),
    },
    {
        "resource_id": "ecs-dev-sandbox-01",
        "name": "developer-sandbox-01",
        "service": "ECS",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "development",
        "owner": "engineering",
        "cost_center": "CC-300",
        "product": "Shared",
        "monthly_cost": 210,
        "pricing_mode": "pay_per_use",
        "vcpu": 4,
        "memory_gb": 16,
        "storage_gb": 100,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "low",
        "tags": {},
        "profile": (2.8, 8, 2, 45, 50),
    },
    {
        "resource_id": "ecs-qa-legacy-01",
        "name": "qa-legacy-runner",
        "service": "ECS",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "qa",
        "owner": "quality-team",
        "cost_center": "CC-300",
        "product": "Shared",
        "monthly_cost": 185,
        "pricing_mode": "pay_per_use",
        "vcpu": 4,
        "memory_gb": 16,
        "storage_gb": 80,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "low",
        "tags": {"expires-on": "2026-08-31"},
        "profile": (12, 22, 7, 45, 55),
    },
    {
        "resource_id": "rds-orders-prod",
        "name": "orders-mysql-prod",
        "service": "RDS",
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "production",
        "owner": "data-platform",
        "cost_center": "CC-200",
        "product": "Commerce",
        "monthly_cost": 690,
        "pricing_mode": "pay_per_use",
        "vcpu": 8,
        "memory_gb": 32,
        "storage_gb": 500,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "mission-critical",
        "tags": {"backup-policy": "gold"},
        "profile": (48, 63, 28, 68, 75),
    },
    {
        "resource_id": "rds-analytics-prod",
        "name": "analytics-postgres-prod",
        "service": "RDS",
        "region": "eu-west-101",
        "enterprise_project": "ep-data",
        "environment": "production",
        "owner": "analytics-team",
        "cost_center": "CC-200",
        "product": "Insights",
        "monthly_cost": 520,
        "pricing_mode": "yearly_monthly",
        "vcpu": 8,
        "memory_gb": 32,
        "storage_gb": 700,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "standard",
        "tags": {"backup-policy": "silver"},
        "profile": (17, 31, 11, 60, 64),
    },
    {
        "resource_id": "evs-orphan-001",
        "name": "detached-migration-volume",
        "service": "EVS",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "development",
        "owner": "platform-team",
        "cost_center": "CC-300",
        "product": "Shared",
        "monthly_cost": 96,
        "pricing_mode": "pay_per_use",
        "vcpu": 0,
        "memory_gb": 0,
        "storage_gb": 1000,
        "status": "available",
        "attached": False,
        "schedule": "24x7",
        "criticality": "low",
        "tags": {"created-by": "migration"},
        "profile": None,
    },
    {
        "resource_id": "eip-unbound-001",
        "name": "legacy-public-ip",
        "service": "EIP",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "development",
        "owner": "network-team",
        "cost_center": "CC-300",
        "product": "Shared",
        "monthly_cost": 38,
        "pricing_mode": "pay_per_use",
        "vcpu": 0,
        "memory_gb": 0,
        "storage_gb": 0,
        "status": "unbound",
        "attached": False,
        "schedule": "24x7",
        "criticality": "low",
        "tags": {},
        "profile": None,
    },
    {
        "resource_id": "obs-platform-logs",
        "name": "central-platform-logs",
        "service": "OBS",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "production",
        "owner": "sre-team",
        "cost_center": "CC-300",
        "product": "Shared",
        "monthly_cost": 275,
        "pricing_mode": "pay_per_use",
        "vcpu": 0,
        "memory_gb": 0,
        "storage_gb": 4200,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "standard",
        "tags": {"retention": "365d"},
        "profile": None,
    },
    {
        "resource_id": "elb-legacy-001",
        "name": "legacy-internal-elb",
        "service": "ELB",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "qa",
        "owner": "network-team",
        "cost_center": "CC-300",
        "product": "Shared",
        "monthly_cost": 82,
        "pricing_mode": "pay_per_use",
        "vcpu": 0,
        "memory_gb": 0,
        "storage_gb": 0,
        "status": "idle",
        "attached": False,
        "schedule": "24x7",
        "criticality": "low",
        "tags": {},
        "profile": None,
    },
    {
        "resource_id": "ecs-ml-prod-01",
        "name": "insights-feature-service",
        "service": "ECS",
        "region": "eu-west-101",
        "enterprise_project": "ep-data",
        "environment": "production",
        "owner": "ml-platform",
        "cost_center": "CC-200",
        "product": "Insights",
        "monthly_cost": 460,
        "pricing_mode": "pay_per_use",
        "vcpu": 8,
        "memory_gb": 32,
        "storage_gb": 200,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "high",
        "tags": {"model": "recommendation-v3"},
        "profile": (44, 55, 35, 66, 72),
    },
    {
        "resource_id": "cce-dev-node-01",
        "name": "cce-dev-node-01",
        "service": "CCE_NODE",
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "development",
        "owner": "sre-team",
        "cost_center": "CC-100",
        "product": "Commerce",
        "monthly_cost": 330,
        "pricing_mode": "pay_per_use",
        "vcpu": 8,
        "memory_gb": 32,
        "storage_gb": 100,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "low",
        "tags": {"cluster": "commerce-dev"},
        "profile": (15, 24, 10, 58, 60),
    },
    {
        "resource_id": "ecs-unallocated-01",
        "name": "temporary-integration-host",
        "service": "ECS",
        "region": "eu-west-101",
        "enterprise_project": "ep-shared",
        "environment": "",
        "owner": "",
        "cost_center": "",
        "product": "",
        "monthly_cost": 145,
        "pricing_mode": "pay_per_use",
        "vcpu": 4,
        "memory_gb": 8,
        "storage_gb": 60,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "standard",
        "tags": {},
        "profile": (23, 36, 18, 50, 52),
    },
]

BUDGETS = [
    ("Cloud Portfolio Monthly", "all", "*", 5800, 85, 100, "USD"),
    ("Commerce Product", "product", "Commerce", 3800, 85, 100, "USD"),
    ("Insights Product", "product", "Insights", 1350, 85, 100, "USD"),
    ("Non-Production", "environment", "development", 550, 80, 100, "USD"),
]


def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def main() -> int:
    randomizer = random.Random(SEED)
    output = Path(__file__).resolve().parents[1] / "data" / "demo"

    resource_rows: list[list[object]] = []
    for resource in RESOURCES:
        resource_rows.append(
            [
                resource["resource_id"],
                resource["name"],
                resource["service"],
                resource["region"],
                resource["enterprise_project"],
                resource["environment"],
                resource["owner"],
                resource["cost_center"],
                resource["product"],
                resource["monthly_cost"],
                resource["pricing_mode"],
                resource["vcpu"],
                resource["memory_gb"],
                resource["storage_gb"],
                resource["status"],
                str(resource["attached"]).lower(),
                resource["schedule"],
                resource["criticality"],
                json.dumps(resource["tags"], separators=(",", ":")),
            ]
        )
    write_csv(
        output / "resources.csv",
        [
            "resource_id",
            "name",
            "service",
            "region",
            "enterprise_project",
            "environment",
            "owner",
            "cost_center",
            "product",
            "monthly_cost",
            "pricing_mode",
            "vcpu",
            "memory_gb",
            "storage_gb",
            "status",
            "attached",
            "schedule",
            "criticality",
            "tags_json",
        ],
        resource_rows,
    )

    cost_rows: list[list[object]] = []
    for day in date_range(START_DATE, END_DATE):
        month_trend = 1 + (day.month - 1) * 0.018
        weekly = 0.95 if day.weekday() >= 5 else 1.02
        days_in_month = (
            date(day.year + (day.month == 12), day.month % 12 + 1, 1)
            - date(day.year, day.month, 1)
        ).days
        for resource in RESOURCES:
            noise = 1 + randomizer.uniform(-0.035, 0.035)
            actual = (
                resource["monthly_cost"] / days_in_month * month_trend * weekly * noise
            )
            if resource["resource_id"] == "cce-prod-node-b" and day == date(
                2026, 5, 18
            ):
                actual *= 2.65
            if resource["resource_id"] == "ecs-ml-prod-01" and day == date(2026, 6, 21):
                actual *= 2.1
            amortized = actual * (
                0.985 if resource["pricing_mode"] != "pay_per_use" else 1
            )
            usage = max(0.1, resource["monthly_cost"] / 10 * weekly)
            cost_rows.append(
                [
                    day.isoformat(),
                    resource["resource_id"],
                    resource["service"],
                    f"{actual:.4f}",
                    f"{amortized:.4f}",
                    f"{usage:.3f}",
                    "USD",
                ]
            )
    write_csv(
        output / "costs.csv",
        [
            "date",
            "resource_id",
            "service",
            "actual_cost",
            "amortized_cost",
            "usage_quantity",
            "currency",
        ],
        cost_rows,
    )

    utilization_rows: list[list[object]] = []
    observation_start = END_DATE - timedelta(days=29)
    for resource in RESOURCES:
        profile = resource["profile"]
        if profile is None:
            continue
        cpu, memory, network, request_cpu, request_memory = profile
        for day in date_range(observation_start, END_DATE):
            for hour in (0, 6, 12, 18):
                business_factor = (
                    1.08 if hour in (12, 18) and day.weekday() < 5 else 0.9
                )
                wave = math.sin((day.toordinal() + hour) / 7) * 2.2

                def value(
                    base: float,
                    spread: float = 4.0,
                    *,
                    factor: float = business_factor,
                    periodic_wave: float = wave,
                ) -> float:
                    result = (
                        base * factor
                        + periodic_wave
                        + randomizer.uniform(-spread, spread)
                    )
                    return round(max(0, min(99.5, result)), 2)

                utilization_rows.append(
                    [
                        datetime.combine(day, time(hour)).isoformat(),
                        resource["resource_id"],
                        value(cpu),
                        value(memory),
                        value(network, 3),
                        value(memory * 0.7, 3),
                        value(request_cpu, 2),
                        value(request_memory, 2),
                    ]
                )
    write_csv(
        output / "utilization.csv",
        [
            "timestamp",
            "resource_id",
            "cpu_pct",
            "memory_pct",
            "network_pct",
            "disk_pct",
            "request_cpu_pct",
            "request_memory_pct",
        ],
        utilization_rows,
    )
    write_csv(
        output / "budgets.csv",
        [
            "name",
            "scope_type",
            "scope_value",
            "monthly_limit",
            "actual_alert_pct",
            "forecast_alert_pct",
            "currency",
        ],
        [list(row) for row in BUDGETS],
    )
    print(
        f"Generated {len(RESOURCES)} resources, {len(cost_rows)} cost records, "
        f"and {len(utilization_rows)} utilization samples in {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
