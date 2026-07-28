from __future__ import annotations

import unittest
from datetime import date

from finops.models import CostRecord, ServiceType
from finops.services.forecast import (
    forecast_monthly_cost,
    latest_month_cost,
    monthly_costs,
)


def monthly_record(month: int, value: float) -> CostRecord:
    return CostRecord(
        record_date=date(2026, month, 1),
        resource_id="ecs-1",
        service=ServiceType.ECS,
        actual_cost=value,
        amortized_cost=value,
        usage_quantity=1,
    )


class ForecastTests(unittest.TestCase):
    def test_monthly_cost_aggregation(self):
        records = [
            monthly_record(1, 100),
            monthly_record(1, 20),
            monthly_record(2, 130),
        ]
        self.assertEqual(
            monthly_costs(records), [("2026-01", 120.0), ("2026-02", 130.0)]
        )

    def test_linear_growth_forecast(self):
        records = [
            monthly_record(month, 100 + (month - 1) * 10) for month in range(1, 7)
        ]
        forecast = forecast_monthly_cost(records, 3)
        self.assertEqual(
            [item.period for item in forecast], ["2026-07", "2026-08", "2026-09"]
        )
        self.assertAlmostEqual(forecast[0].predicted_cost, 160, places=2)

    def test_forecast_has_ordered_bounds(self):
        forecast = forecast_monthly_cost(
            [monthly_record(month, 100 + month * 3) for month in range(1, 5)],
            1,
        )[0]
        self.assertLessEqual(forecast.lower_bound, forecast.predicted_cost)
        self.assertGreaterEqual(forecast.upper_bound, forecast.predicted_cost)

    def test_forecast_empty(self):
        self.assertEqual(forecast_monthly_cost([], 2), [])

    def test_forecast_rejects_invalid_horizon(self):
        with self.assertRaises(ValueError):
            forecast_monthly_cost([monthly_record(1, 100)], 0)

    def test_latest_month_cost(self):
        self.assertEqual(
            latest_month_cost([monthly_record(1, 100), monthly_record(2, 130)]),
            130,
        )


if __name__ == "__main__":
    unittest.main()
