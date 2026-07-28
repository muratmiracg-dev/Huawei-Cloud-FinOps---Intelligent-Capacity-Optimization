"""Domain models shared by collectors, optimizers, APIs, and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any


class ServiceType(StrEnum):
    ECS = "ECS"
    CCE_NODE = "CCE_NODE"
    EVS = "EVS"
    EIP = "EIP"
    RDS = "RDS"
    OBS = "OBS"
    ELB = "ELB"
    OTHER = "OTHER"


class PricingMode(StrEnum):
    PAY_PER_USE = "pay_per_use"
    YEARLY_MONTHLY = "yearly_monthly"
    SAVINGS_PLAN = "savings_plan"


class RecommendationType(StrEnum):
    RIGHTSIZE = "rightsize"
    IDLE_RESOURCE = "idle_resource"
    SCHEDULE = "schedule"
    COMMITMENT = "commitment"
    STORAGE_LIFECYCLE = "storage_lifecycle"
    TAGGING = "tagging"
    CAPACITY_RISK = "capacity_risk"
    REQUEST_TUNING = "request_tuning"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class CloudResource:
    resource_id: str
    name: str
    service: ServiceType
    region: str
    enterprise_project: str
    environment: str
    owner: str
    cost_center: str
    product: str
    monthly_cost: float
    pricing_mode: PricingMode = PricingMode.PAY_PER_USE
    vcpu: int = 0
    memory_gb: float = 0.0
    storage_gb: float = 0.0
    status: str = "active"
    attached: bool = True
    schedule: str = "24x7"
    criticality: str = "standard"
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CostRecord:
    record_date: date
    resource_id: str
    service: ServiceType
    actual_cost: float
    amortized_cost: float
    usage_quantity: float
    currency: str = "USD"


@dataclass(frozen=True, slots=True)
class UtilizationSample:
    timestamp: datetime
    resource_id: str
    cpu_pct: float = 0.0
    memory_pct: float = 0.0
    network_pct: float = 0.0
    disk_pct: float = 0.0
    request_cpu_pct: float = 0.0
    request_memory_pct: float = 0.0


@dataclass(frozen=True, slots=True)
class Budget:
    name: str
    scope_type: str
    scope_value: str
    monthly_limit: float
    actual_alert_pct: float = 85.0
    forecast_alert_pct: float = 100.0
    currency: str = "USD"


@dataclass(frozen=True, slots=True)
class Recommendation:
    recommendation_id: str
    resource_id: str
    resource_name: str
    service: ServiceType
    recommendation_type: RecommendationType
    action: str
    rationale: str
    current_monthly_cost: float
    estimated_monthly_savings: float
    estimated_savings_pct: float
    risk: RiskLevel
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CostAnomaly:
    resource_id: str
    anomaly_date: date
    actual_cost: float
    expected_cost: float
    deviation_pct: float
    score: float
    severity: RiskLevel


@dataclass(frozen=True, slots=True)
class ForecastPoint:
    period: str
    predicted_cost: float
    lower_bound: float
    upper_bound: float


@dataclass(frozen=True, slots=True)
class BudgetStatus:
    name: str
    scope_type: str
    scope_value: str
    monthly_limit: float
    month_to_date_cost: float
    forecast_cost: float
    utilization_pct: float
    forecast_utilization_pct: float
    status: str


@dataclass(frozen=True, slots=True)
class FinOpsSummary:
    current_monthly_cost: float
    estimated_monthly_savings: float
    savings_opportunity_pct: float
    annualized_savings: float
    allocation_coverage_pct: float
    budget_coverage_pct: float
    recommendation_count: int
    high_risk_count: int
    anomaly_count: int
    maturity_score: float
    currency: str = "USD"


def model_to_dict(value: Any) -> dict[str, Any]:
    """Convert a dataclass model into a JSON-friendly dictionary."""

    result = asdict(value)
    for key, item in tuple(result.items()):
        if isinstance(item, (date, datetime)):
            result[key] = item.isoformat()
        elif isinstance(item, StrEnum):
            result[key] = str(item)
    return result
