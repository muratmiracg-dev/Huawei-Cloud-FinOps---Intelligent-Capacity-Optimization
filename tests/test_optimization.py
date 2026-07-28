from __future__ import annotations

import unittest

from finops.models import (
    PricingMode,
    RecommendationType,
    RiskLevel,
    ServiceType,
)
from finops.services.optimization import (
    generate_recommendations,
    non_overlapping_savings,
)
from tests.fixtures import resource, samples


class OptimizationTests(unittest.TestCase):
    def types(self, recommendations):
        return {item.recommendation_type for item in recommendations}

    def test_rightsize_low_utilization(self):
        recommendations = generate_recommendations(
            [resource()],
            samples(cpu=20, memory=30),
        )
        self.assertIn(RecommendationType.RIGHTSIZE, self.types(recommendations))

    def test_nonprod_idle_resource(self):
        item = resource(environment="development")
        recommendations = generate_recommendations(
            [item],
            samples(cpu=2, memory=5, network=2),
        )
        self.assertIn(RecommendationType.IDLE_RESOURCE, self.types(recommendations))

    def test_capacity_risk(self):
        recommendations = generate_recommendations(
            [resource()],
            samples(cpu=92, memory=70),
        )
        risks = [
            item
            for item in recommendations
            if item.recommendation_type == RecommendationType.CAPACITY_RISK
        ]
        self.assertEqual(risks[0].risk, RiskLevel.HIGH)

    def test_unattached_evs(self):
        item = resource(
            service=ServiceType.EVS,
            attached=False,
            status="available",
            monthly_cost=50,
        )
        recommendations = generate_recommendations([item], [])
        self.assertIn(RecommendationType.IDLE_RESOURCE, self.types(recommendations))

    def test_obs_lifecycle(self):
        item = resource(
            service=ServiceType.OBS,
            storage_gb=1000,
            monthly_cost=100,
        )
        recommendations = generate_recommendations([item], [])
        self.assertIn(RecommendationType.STORAGE_LIFECYCLE, self.types(recommendations))

    def test_nonprod_schedule(self):
        item = resource(environment="qa", schedule="24x7")
        recommendations = generate_recommendations(
            [item],
            samples(cpu=45, memory=55),
        )
        self.assertIn(RecommendationType.SCHEDULE, self.types(recommendations))

    def test_production_commitment(self):
        item = resource(
            environment="production",
            pricing_mode=PricingMode.PAY_PER_USE,
        )
        recommendations = generate_recommendations(
            [item],
            samples(cpu=50, memory=55),
        )
        self.assertIn(RecommendationType.COMMITMENT, self.types(recommendations))

    def test_cce_request_tuning(self):
        item = resource(service=ServiceType.CCE_NODE)
        recommendations = generate_recommendations(
            [item],
            samples(
                cpu=20,
                memory=30,
                request_cpu=70,
                request_memory=75,
            ),
        )
        self.assertIn(RecommendationType.REQUEST_TUNING, self.types(recommendations))

    def test_tagging_recommendation(self):
        item = resource(owner="", cost_center="", product="", environment="")
        recommendations = generate_recommendations([item], samples())
        self.assertIn(RecommendationType.TAGGING, self.types(recommendations))

    def test_minimum_savings_filter(self):
        item = resource(monthly_cost=1)
        recommendations = generate_recommendations(
            [item],
            samples(cpu=20, memory=30),
            minimum_savings=5,
        )
        self.assertNotIn(RecommendationType.RIGHTSIZE, self.types(recommendations))

    def test_non_overlapping_savings_uses_largest_per_resource(self):
        item = resource(environment="development", monthly_cost=100)
        recommendations = generate_recommendations(
            [item],
            samples(cpu=2, memory=5, network=2),
            minimum_savings=0,
        )
        self.assertEqual(
            non_overlapping_savings(recommendations),
            max(entry.estimated_monthly_savings for entry in recommendations),
        )


if __name__ == "__main__":
    unittest.main()
