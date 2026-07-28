from __future__ import annotations

import unittest
from datetime import date, timedelta

from finops.models import CostRecord, RiskLevel, ServiceType
from finops.services.anomaly import detect_cost_anomalies


def record(day: date, value: float) -> CostRecord:
    return CostRecord(
        record_date=day,
        resource_id="ecs-1",
        service=ServiceType.ECS,
        actual_cost=value,
        amortized_cost=value,
        usage_quantity=1,
    )


class AnomalyTests(unittest.TestCase):
    def test_requires_minimum_history(self):
        start = date(2026, 1, 1)
        records = [record(start + timedelta(days=index), 10) for index in range(6)]
        records.append(record(start + timedelta(days=6), 100))
        self.assertEqual(detect_cost_anomalies(records), [])

    def test_detects_large_spike(self):
        start = date(2026, 1, 1)
        records = [
            record(start + timedelta(days=index), 10 + (index % 2) * 0.2)
            for index in range(10)
        ]
        records.append(record(start + timedelta(days=10), 25))
        anomalies = detect_cost_anomalies(records)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].severity, RiskLevel.CRITICAL)

    def test_ignores_small_deviation(self):
        start = date(2026, 1, 1)
        records = [record(start + timedelta(days=index), 10) for index in range(10)]
        records.append(record(start + timedelta(days=10), 11))
        self.assertEqual(detect_cost_anomalies(records), [])

    def test_aggregates_same_day_records(self):
        start = date(2026, 1, 1)
        records = []
        for index in range(8):
            records.extend(
                [
                    record(start + timedelta(days=index), 5),
                    record(start + timedelta(days=index), 5),
                ]
            )
        records.append(record(start + timedelta(days=8), 30))
        self.assertEqual(len(detect_cost_anomalies(records)), 1)


if __name__ == "__main__":
    unittest.main()
