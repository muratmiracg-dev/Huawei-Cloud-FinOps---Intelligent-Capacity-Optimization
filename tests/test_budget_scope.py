"""Budget status must come from each scope's own billing records."""

from __future__ import annotations

import unittest
from datetime import date

from finops.services.budgets import evaluate_budgets
from tests.fixtures import budget, costs, resource


def _by_name(statuses):
    return {status.name: status for status in statuses}


class BudgetScopeAttributionTests(unittest.TestCase):
    def setUp(self):
        # Equal inventory baselines, very different real spend.
        self.resources = [
            resource(resource_id="web", product="Commerce", monthly_cost=100),
            resource(resource_id="ml", product="Insights", monthly_cost=100),
        ]
        start = date(2026, 5, 1)
        self.costs = costs("web", daily=3, days=61, start=start) + costs(
            "ml", daily=10, days=61, start=start
        )
        self.budgets = [
            budget(
                name="Commerce",
                scope_type="product",
                scope_value="Commerce",
                monthly_limit=200,
            ),
            budget(
                name="Insights",
                scope_type="product",
                scope_value="Insights",
                monthly_limit=200,
            ),
            budget(name="All", monthly_limit=1000),
        ]

    def test_spike_is_charged_to_the_scope_that_caused_it(self):
        statuses = _by_name(evaluate_budgets(self.resources, self.costs, self.budgets))

        # June: web 30 x 3 = 90, ml 30 x 10 = 300.
        self.assertEqual(statuses["Commerce"].month_to_date_cost, 90.0)
        self.assertEqual(statuses["Commerce"].status, "healthy")
        self.assertEqual(statuses["Insights"].month_to_date_cost, 300.0)
        self.assertEqual(statuses["Insights"].status, "breached")
        # The old share-of-inventory method reported 195.0 / 97.5% for both.
        self.assertNotEqual(
            statuses["Commerce"].month_to_date_cost,
            statuses["Insights"].month_to_date_cost,
        )

    def test_scope_forecast_uses_scope_history(self):
        statuses = _by_name(evaluate_budgets(self.resources, self.costs, self.budgets))

        # May has 31 days and June 30, so each scope trends down by one day.
        self.assertAlmostEqual(statuses["Commerce"].forecast_cost, 87.0)
        self.assertAlmostEqual(statuses["Insights"].forecast_cost, 290.0)
        self.assertAlmostEqual(statuses["All"].forecast_cost, 377.0)

    def test_scope_without_spend_in_latest_month_reports_zero(self):
        resources = [*self.resources, resource(resource_id="old", product="Legacy")]
        old_costs = costs("old", daily=50, days=10, start=date(2026, 5, 1))
        statuses = _by_name(
            evaluate_budgets(
                resources,
                self.costs + old_costs,
                [
                    budget(
                        name="Legacy",
                        scope_type="product",
                        scope_value="Legacy",
                        monthly_limit=100,
                    )
                ],
            )
        )

        # Legacy spent only in May; June (the portfolio's latest month) is zero and
        # the zero month enters the forecast instead of being skipped.
        self.assertEqual(statuses["Legacy"].month_to_date_cost, 0.0)
        self.assertEqual(statuses["Legacy"].forecast_cost, 0.0)
        self.assertEqual(statuses["Legacy"].status, "healthy")

    def test_unknown_resources_count_only_in_portfolio_budget(self):
        orphan = costs("unregistered", daily=5, days=30, start=date(2026, 6, 1))
        statuses = _by_name(
            evaluate_budgets(self.resources, self.costs + orphan, self.budgets)
        )

        self.assertEqual(statuses["All"].month_to_date_cost, 540.0)
        self.assertEqual(statuses["Commerce"].month_to_date_cost, 90.0)
        self.assertEqual(statuses["Insights"].month_to_date_cost, 300.0)

    def test_budget_with_no_matching_resources(self):
        statuses = evaluate_budgets(
            self.resources,
            self.costs,
            [
                budget(
                    name="Empty",
                    scope_type="product",
                    scope_value="Nothing",
                    monthly_limit=100,
                )
            ],
        )

        self.assertEqual(statuses[0].month_to_date_cost, 0.0)
        self.assertEqual(statuses[0].forecast_cost, 0.0)
        self.assertEqual(statuses[0].status, "healthy")


if __name__ == "__main__":
    unittest.main()
