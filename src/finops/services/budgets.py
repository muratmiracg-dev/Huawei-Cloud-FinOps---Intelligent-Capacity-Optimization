"""Budget coverage and breach forecasting."""

from __future__ import annotations

from collections.abc import Sequence

from finops.models import Budget, BudgetStatus, CloudResource, CostRecord
from finops.services.forecast import forecast_monthly_series, monthly_costs


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


def _scoped_costs(
    resources: Sequence[CloudResource],
    costs: Sequence[CostRecord],
    budget: Budget,
) -> list[CostRecord]:
    """Cost records that belong to the budget's scope.

    Scopes are defined on inventory attributes, so a record is in scope when its
    resource matches. Records for resources missing from the inventory can only be
    attributed to the portfolio-wide ``all`` scope.
    """

    if budget.scope_type == "all":
        return list(costs)
    in_scope = {
        resource.resource_id for resource in resources if _matches(resource, budget)
    }
    return [record for record in costs if record.resource_id in in_scope]


def evaluate_budgets(
    resources: Sequence[CloudResource],
    costs: Sequence[CostRecord],
    budgets: Sequence[Budget],
) -> list[BudgetStatus]:
    """Compare each scope's billed cost and next-month forecast with its limit.

    Actual and forecast cost come from the scope's own billing records. Earlier
    versions apportioned the portfolio total by each scope's share of inventory
    ``monthly_cost``, which spread a spike in one product or environment across
    every budget and could hide the breach in the scope that caused it.
    """

    portfolio_periods = [period for period, _ in monthly_costs(costs)]

    statuses: list[BudgetStatus] = []
    for budget in budgets:
        scoped = dict(monthly_costs(_scoped_costs(resources, costs, budget)))
        # Align the scope's history to the portfolio calendar from its first billed
        # month, so months without spend count as zero instead of being skipped.
        history = [
            (period, scoped.get(period, 0.0))
            for period in portfolio_periods
            if scoped and period >= min(scoped)
        ]
        actual = history[-1][1] if history else 0.0
        forecast = forecast_monthly_series(history, 1)
        predicted = forecast[0].predicted_cost if forecast else 0.0
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
