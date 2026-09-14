from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from finops.adapters.csv_repository import CsvRepository, _bool
from finops.adapters.huawei_billing import normalize_billing_records
from finops.engine import FinOpsEngine
from finops.telemetry import render_metrics


class AdapterAndTelemetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).resolve().parents[1] / "data" / "demo"

    def test_demo_csv_repository_loads_all_contracts(self):
        repo = CsvRepository(self.data_dir)
        self.assertGreater(len(repo.resources()), 10)
        self.assertGreater(len(repo.costs()), 1000)
        self.assertGreater(len(repo.utilization()), 1000)
        self.assertGreater(len(repo.budgets()), 1)

    def test_csv_boolean_parser_accepts_documented_values(self):
        for value in ("true", "TRUE", " yes ", "y", "1"):
            with self.subTest(value=value):
                self.assertTrue(_bool(value))
        for value in ("false", "FALSE", " no ", "n", "0"):
            with self.subTest(value=value):
                self.assertFalse(_bool(value))

    def test_csv_boolean_parser_rejects_ambiguous_values(self):
        for value in ("", "2", "unknown", "tru"):
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "Invalid boolean value"),
            ):
                _bool(value)

    def test_huawei_export_normalization(self):
        records = normalize_billing_records(
            [
                {
                    "Usage Date": "2026-06-01",
                    "Resource ID": "ecs-1",
                    "Service Type": "Elastic Cloud Server",
                    "Net Amount": "12.5",
                    "Amortized Net Amount": "11.8",
                    "Usage": "24",
                    "Currency": "USD",
                }
            ]
        )
        self.assertEqual(records[0].record_date, date(2026, 6, 1))
        self.assertEqual(records[0].resource_id, "ecs-1")
        self.assertEqual(records[0].amortized_cost, 11.8)

    def test_unknown_huawei_service_maps_to_other(self):
        records = normalize_billing_records(
            [
                {
                    "date": "2026-06-01",
                    "resource_id": "x",
                    "service_type": "Future Service",
                    "actual_cost": 1,
                }
            ]
        )
        self.assertEqual(records[0].service.value, "OTHER")

    def test_prometheus_metrics_have_type_and_values(self):
        summary = FinOpsEngine(CsvRepository(self.data_dir)).summary()
        metrics = render_metrics(summary)
        self.assertIn("# TYPE finops_current_monthly_cost gauge", metrics)
        self.assertIn("finops_maturity_score", metrics)


if __name__ == "__main__":
    unittest.main()
