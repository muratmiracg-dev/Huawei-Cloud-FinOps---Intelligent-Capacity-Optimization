"""A month that is still in progress must not be read as a full month of spend."""

from __future__ import annotations

import unittest
from datetime import date

from finops.engine import FinOpsEngine
from finops.models import CostRecord, ServiceType
from finops.repository import InMemoryRepository
from finops.services.budgets import evaluate_budgets
from finops.services.forecast import (
    first_month_completion_ratio,
    forecast_monthly_cost,
    latest_month_run_rate,
    month_completion_ratio,
)
from tests.fixtures import budget, costs, resource, samples

# Flat 10/day from 1 April to 15 June: April and May are complete, June is half done.
DAILY_TO_MID_JUNE = costs(daily=10, days=76, start=date(2026, 4, 1))


def _monthly(month: int, value: float) -> CostRecord:
    return CostRecord(
        record_date=date(2026, month, 1),
        resource_id="ecs-1",
        service=ServiceType.ECS,
        actual_cost=value,
        amortized_cost=value,
        usage_quantity=1,
    )


class MonthCompletionTests(unittest.TestCase):
    def test_daily_export_ending_mid_month_is_partial(self):
        self.assertEqual(month_completion_ratio(DAILY_TO_MID_JUNE), 0.5)

    def test_complete_daily_month_is_complete(self):
        records = costs(daily=10, days=91, start=date(2026, 4, 1))  # to 30 June
        self.assertEqual(month_completion_ratio(records), 1.0)

    def test_monthly_export_is_never_scaled(self):
        records = [_monthly(4, 300), _monthly(5, 310), _monthly(6, 320)]
        self.assertEqual(month_completion_ratio(records), 1.0)

    def test_single_month_and_empty_inputs_are_complete(self):
        self.assertEqual(
            month_completion_ratio(costs(days=10, start=date(2026, 6, 1))), 1.0
        )
        self.assertEqual(month_completion_ratio([]), 1.0)


class PartialMonthDecisionTests(unittest.TestCase):
    def test_forecast_does_not_read_month_to_date_as_a_cost_drop(self):
        forecast = forecast_monthly_cost(DAILY_TO_MID_JUNE, 1)[0]
        # Flat spend: about 300 per month. Month-to-date June (150) used to drag the
        # trend down to a July forecast of roughly 105.
        self.assertEqual(forecast.period, "2026-07")
        self.assertAlmostEqual(forecast.predicted_cost, 300, delta=10)

    def test_current_monthly_cost_is_a_full_month_run_rate(self):
        self.assertEqual(latest_month_run_rate(DAILY_TO_MID_JUNE), 300.0)
        repo = InMemoryRepository(
            resource_records=[resource(monthly_cost=300)],
            cost_records=DAILY_TO_MID_JUNE,
            utilization_records=samples(cpu=20, memory=30),
            budget_records=[budget(monthly_limit=1000)],
        )
        summary = FinOpsEngine(repo).summary()
        self.assertEqual(summary.current_monthly_cost, 300.0)
        # Full-month savings over a full-month baseline, not over half a month.
        self.assertAlmostEqual(
            summary.savings_opportunity_pct,
            summary.estimated_monthly_savings / 300 * 100,
            places=2,
        )

    def test_budget_forecast_breach_is_not_hidden_by_a_partial_month(self):
        [status] = evaluate_budgets(
            [resource(monthly_cost=300)],
            DAILY_TO_MID_JUNE,
            [budget(monthly_limit=320, forecast_alert_pct=90)],
        )
        self.assertEqual(status.month_to_date_cost, 150.0)
        self.assertAlmostEqual(status.forecast_cost, 300, delta=10)
        self.assertEqual(status.status, "forecast_breach")


if __name__ == "__main__":
    unittest.main()


# Flat 10/day from 15 March to 30 June: March is half covered, April to June are complete.
DAILY_FROM_MID_MARCH = costs(daily=10, days=108, start=date(2026, 3, 15))


class PartialFirstMonthTests(unittest.TestCase):
    def test_daily_export_starting_mid_month_is_partial(self):
        self.assertAlmostEqual(
            first_month_completion_ratio(DAILY_FROM_MID_MARCH), 17 / 31
        )
        self.assertEqual(month_completion_ratio(DAILY_FROM_MID_MARCH), 1.0)

    def test_monthly_export_first_month_is_never_scaled(self):
        records = [_monthly(4, 300), _monthly(5, 310), _monthly(6, 320)]
        self.assertEqual(first_month_completion_ratio(records), 1.0)

    def test_forecast_does_not_read_a_partial_first_month_as_growth(self):
        forecast = forecast_monthly_cost(DAILY_FROM_MID_MARCH, 1)[0]
        # Flat spend of about 300 per month. The 170 of half-covered March used to tilt
        # the trend upward to a July forecast of roughly 375.
        self.assertEqual(forecast.period, "2026-07")
        self.assertAlmostEqual(forecast.predicted_cost, 305, delta=10)
