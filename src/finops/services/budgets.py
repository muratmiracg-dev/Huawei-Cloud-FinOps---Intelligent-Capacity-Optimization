"""Budget coverage and breach forecasting."""

from __future__ import annotations

from collections.abc import Sequence

from finops.models import Budget, BudgetStatus, CloudResource, CostRecord
from finops.services.forecast import forecast_monthly_cost, latest_month_cost


def _matches(resource: CloudResource, budget: Budget) -> bool:
    if budget.scope_type == "all":
        return True
    value = getattr(resource, budget.scope_type, "")
    if hasattr(value, "value"):
        value = value.value
    return str(value) == budget.scope_value


def budget_coverage(
    resources: Sequence[CloudResource], budgets: Sequence[Budget]
) -> float:
    total = sum(resource.monthly_cost for resource in resources)
    if total <= 0:
        return 100.0
    covered_ids = {
        resource.resource_id
        for resource in resources
        if any(_matches(resource, budget) for budget in budgets)
    }
    covered = sum(
        resource.monthly_cost
        for resource in resources
        if resource.resource_id in covered_ids
    )
    return round(covered / total * 100, 2)


def evaluate_budgets(
    resources: Sequence[CloudResource],
    costs: Sequence[CostRecord],
    budgets: Sequence[Budget],
) -> list[BudgetStatus]:
    latest_cost = latest_month_cost(costs)
    total_baseline = sum(resource.monthly_cost for resource in resources)
    forecast = forecast_monthly_cost(costs, 1)
    total_forecast = forecast[0].predicted_cost if forecast else latest_cost

    statuses: list[BudgetStatus] = []
    for budget in budgets:
        scoped_cost = sum(
            resource.monthly_cost
            for resource in resources
            if _matches(resource, budget)
        )
        share = scoped_cost / total_baseline if total_baseline else 0.0
        actual = latest_cost * share
        predicted = total_forecast * share
        actual_pct = actual / budget.monthly_limit * 100 if budget.monthly_limit else 0
        forecast_pct = (
            predicted / budget.monthly_limit * 100 if budget.monthly_limit else 0
        )
        status = (
            "breached"
            if actual_pct >= 100
            else "forecast_breach"
            if forecast_pct >= budget.forecast_alert_pct
            else "warning"
            if actual_pct >= budget.actual_alert_pct
            else "healthy"
        )
        statuses.append(
            BudgetStatus(
                name=budget.name,
                scope_type=budget.scope_type,
                scope_value=budget.scope_value,
                monthly_limit=round(budget.monthly_limit, 2),
                month_to_date_cost=round(actual, 2),
                forecast_cost=round(predicted, 2),
                utilization_pct=round(actual_pct, 2),
                forecast_utilization_pct=round(forecast_pct, 2),
                status=status,
            )
        )
    return sorted(
        statuses, key=lambda item: item.forecast_utilization_pct, reverse=True
    )
