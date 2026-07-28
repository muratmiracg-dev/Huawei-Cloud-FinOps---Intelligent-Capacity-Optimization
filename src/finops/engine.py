"""Application service orchestrating the FinOps decision loop."""

from __future__ import annotations

from finops.models import (
    BudgetStatus,
    CostAnomaly,
    FinOpsSummary,
    ForecastPoint,
    Recommendation,
)
from finops.repository import FinOpsRepository
from finops.services.allocation import allocation_by, allocation_coverage
from finops.services.anomaly import detect_cost_anomalies
from finops.services.budgets import budget_coverage, evaluate_budgets
from finops.services.forecast import forecast_monthly_cost, latest_month_cost
from finops.services.maturity import calculate_maturity_score
from finops.services.optimization import (
    generate_recommendations,
    non_overlapping_savings,
)


class FinOpsEngine:
    def __init__(
        self,
        repository: FinOpsRepository,
        *,
        minimum_savings: float = 5.0,
        headroom_pct: float = 25.0,
    ):
        self.repository = repository
        self.minimum_savings = minimum_savings
        self.headroom_pct = headroom_pct

    def recommendations(self) -> list[Recommendation]:
        return generate_recommendations(
            self.repository.resources(),
            self.repository.utilization(),
            minimum_savings=self.minimum_savings,
            headroom_pct=self.headroom_pct,
        )

    def anomalies(self) -> list[CostAnomaly]:
        return detect_cost_anomalies(self.repository.costs())

    def forecast(self, months: int = 3) -> list[ForecastPoint]:
        return forecast_monthly_cost(self.repository.costs(), months)

    def allocation(self, dimension: str = "product") -> dict[str, float]:
        return allocation_by(self.repository.resources(), dimension)

    def budget_statuses(self) -> list[BudgetStatus]:
        return evaluate_budgets(
            self.repository.resources(),
            self.repository.costs(),
            self.repository.budgets(),
        )

    def summary(self) -> FinOpsSummary:
        resources = self.repository.resources()
        costs = self.repository.costs()
        budgets = self.repository.budgets()
        recommendations = self.recommendations()
        anomalies = self.anomalies()
        current_cost = latest_month_cost(costs)
        savings = non_overlapping_savings(recommendations)
        allocation_pct = allocation_coverage(resources)
        budget_pct = budget_coverage(resources, budgets)
        maturity = calculate_maturity_score(
            allocation_coverage_pct=allocation_pct,
            budget_coverage_pct=budget_pct,
            recommendations=recommendations,
            anomaly_count=len(anomalies),
        )
        return FinOpsSummary(
            current_monthly_cost=round(current_cost, 2),
            estimated_monthly_savings=savings,
            savings_opportunity_pct=round(
                savings / current_cost * 100 if current_cost else 0.0, 2
            ),
            annualized_savings=round(savings * 12, 2),
            allocation_coverage_pct=allocation_pct,
            budget_coverage_pct=budget_pct,
            recommendation_count=len(recommendations),
            high_risk_count=sum(
                item.risk.value in {"high", "critical"} for item in recommendations
            ),
            anomaly_count=len(anomalies),
            maturity_score=maturity,
        )

    def full_analysis(self, forecast_months: int = 3) -> dict[str, object]:
        return {
            "summary": self.summary(),
            "recommendations": self.recommendations(),
            "anomalies": self.anomalies(),
            "forecast": self.forecast(forecast_months),
            "budgets": self.budget_statuses(),
            "allocation": {
                dimension: self.allocation(dimension)
                for dimension in (
                    "service",
                    "enterprise_project",
                    "environment",
                    "cost_center",
                    "product",
                )
            },
        }
