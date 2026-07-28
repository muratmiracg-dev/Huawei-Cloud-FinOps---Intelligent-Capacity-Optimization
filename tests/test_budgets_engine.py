from __future__ import annotations

import unittest

from finops.engine import FinOpsEngine
from finops.repository import InMemoryRepository
from finops.services.budgets import budget_coverage, evaluate_budgets
from tests.fixtures import budget, costs, resource, samples


class BudgetAndEngineTests(unittest.TestCase):
    def test_budget_coverage_all(self):
        self.assertEqual(budget_coverage([resource()], [budget()]), 100)

    def test_budget_coverage_partial(self):
        resources = [
            resource(resource_id="a", product="Commerce", monthly_cost=75),
            resource(resource_id="b", product="Insights", monthly_cost=25),
        ]
        budgets = [budget(scope_type="product", scope_value="Commerce")]
        self.assertEqual(budget_coverage(resources, budgets), 75)

    def test_budget_status_breached(self):
        statuses = evaluate_budgets(
            [resource(monthly_cost=100)],
            costs(daily=20, days=31),
            [budget(monthly_limit=100)],
        )
        self.assertEqual(statuses[0].status, "breached")

    def test_engine_summary(self):
        repo = InMemoryRepository(
            resource_records=[resource()],
            cost_records=costs(daily=10, days=40),
            utilization_records=samples(cpu=20, memory=30),
            budget_records=[budget()],
        )
        summary = FinOpsEngine(repo).summary()
        self.assertGreater(summary.current_monthly_cost, 0)
        self.assertGreater(summary.estimated_monthly_savings, 0)
        self.assertEqual(summary.budget_coverage_pct, 100)

    def test_full_analysis_contains_decision_domains(self):
        repo = InMemoryRepository(
            resource_records=[resource()],
            cost_records=costs(),
            utilization_records=samples(),
            budget_records=[budget()],
        )
        analysis = FinOpsEngine(repo).full_analysis(2)
        self.assertEqual(
            set(analysis),
            {
                "summary",
                "recommendations",
                "anomalies",
                "forecast",
                "budgets",
                "allocation",
            },
        )
        self.assertEqual(len(analysis["forecast"]), 2)


if __name__ == "__main__":
    unittest.main()
