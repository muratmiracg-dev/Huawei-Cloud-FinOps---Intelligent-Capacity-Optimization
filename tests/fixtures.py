from __future__ import annotations

from datetime import date, datetime, timedelta

from finops.models import (
    Budget,
    CloudResource,
    CostRecord,
    PricingMode,
    ServiceType,
    UtilizationSample,
)


def resource(**overrides) -> CloudResource:
    values = {
        "resource_id": "ecs-1",
        "name": "web-1",
        "service": ServiceType.ECS,
        "region": "eu-west-101",
        "enterprise_project": "ep-commerce",
        "environment": "production",
        "owner": "platform",
        "cost_center": "CC-100",
        "product": "Commerce",
        "monthly_cost": 100.0,
        "pricing_mode": PricingMode.PAY_PER_USE,
        "vcpu": 4,
        "memory_gb": 16.0,
        "storage_gb": 100.0,
        "status": "active",
        "attached": True,
        "schedule": "24x7",
        "criticality": "standard",
        "tags": {},
    }
    values.update(overrides)
    return CloudResource(**values)


def samples(
    resource_id: str = "ecs-1",
    *,
    cpu: float = 20,
    memory: float = 30,
    network: float = 15,
    request_cpu: float = 55,
    request_memory: float = 60,
    days: int = 30,
) -> list[UtilizationSample]:
    start = datetime(2026, 6, 1)
    return [
        UtilizationSample(
            timestamp=start + timedelta(days=index),
            resource_id=resource_id,
            cpu_pct=cpu,
            memory_pct=memory,
            network_pct=network,
            disk_pct=20,
            request_cpu_pct=request_cpu,
            request_memory_pct=request_memory,
        )
        for index in range(days)
    ]


def costs(
    resource_id: str = "ecs-1",
    *,
    daily: float = 10,
    days: int = 40,
    start: date = date(2026, 5, 1),
) -> list[CostRecord]:
    return [
        CostRecord(
            record_date=start + timedelta(days=index),
            resource_id=resource_id,
            service=ServiceType.ECS,
            actual_cost=daily,
            amortized_cost=daily,
            usage_quantity=1,
        )
        for index in range(days)
    ]


def budget(**overrides) -> Budget:
    values = {
        "name": "All",
        "scope_type": "all",
        "scope_value": "*",
        "monthly_limit": 500,
    }
    values.update(overrides)
    return Budget(**values)
