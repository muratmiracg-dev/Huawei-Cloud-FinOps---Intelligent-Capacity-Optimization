from __future__ import annotations

import unittest

from finops.services.allocation import (
    allocation_by,
    allocation_coverage,
    tag_compliance,
)
from tests.fixtures import resource


class AllocationTests(unittest.TestCase):
    def test_allocation_groups_cost(self):
        items = [
            resource(resource_id="a", product="Commerce", monthly_cost=100),
            resource(resource_id="b", product="Commerce", monthly_cost=50),
            resource(resource_id="c", product="Insights", monthly_cost=80),
        ]
        self.assertEqual(
            allocation_by(items, "product"),
            {"Commerce": 150.0, "Insights": 80.0},
        )

    def test_allocation_rejects_unknown_dimension(self):
        with self.assertRaises(ValueError):
            allocation_by([resource()], "password")

    def test_full_allocation_coverage(self):
        self.assertEqual(allocation_coverage([resource()]), 100)

    def test_weighted_allocation_coverage(self):
        items = [
            resource(resource_id="a", monthly_cost=75),
            resource(
                resource_id="b",
                monthly_cost=25,
                owner="",
                cost_center="",
                product="",
            ),
        ]
        self.assertEqual(allocation_coverage(items), 75)

    def test_tag_compliance_detects_missing_canonical_values(self):
        valid, missing = tag_compliance(
            resource(owner="", cost_center="", product="", environment="")
        )
        self.assertFalse(valid)
        self.assertEqual(
            set(missing), {"owner", "cost-center", "product", "environment"}
        )

    def test_tag_can_satisfy_missing_canonical_value(self):
        valid, missing = tag_compliance(
            resource(
                owner="",
                tags={"owner": "platform"},
            )
        )
        self.assertTrue(valid)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
