from __future__ import annotations

from fastapi.testclient import TestClient

from finops.api import build_app
from finops.repository import InMemoryRepository
from tests.fixtures import budget, costs, resource, samples


def client() -> TestClient:
    repository = InMemoryRepository(
        resource_records=[resource(monthly_cost=500)],
        cost_records=costs(daily=20, days=40),
        utilization_records=samples(cpu=12, memory=20),
        budget_records=[budget(monthly_limit=1_000)],
    )
    return TestClient(build_app(repository))


def test_health_endpoints_report_readiness() -> None:
    api = client()

    assert api.get("/health/live").json() == {"status": "alive"}
    assert api.get("/health/ready").json() == {
        "status": "ready",
        "resources": 1,
    }


def test_summary_and_metrics_expose_decision_signals() -> None:
    api = client()

    summary = api.get("/api/v1/summary")
    metrics = api.get("/metrics")

    assert summary.status_code == 200
    assert summary.json()["recommendation_count"] >= 1
    assert summary.json()["currency"] == "USD"
    assert metrics.status_code == 200
    assert "# TYPE finops_current_monthly_cost gauge" in metrics.text


def test_recommendation_filter_respects_minimum_savings() -> None:
    response = client().get("/api/v1/recommendations?min_savings=10000")

    assert response.status_code == 200
    assert response.json() == []


def test_forecast_validates_supported_horizon() -> None:
    api = client()

    assert api.get("/api/v1/forecast?months=2").status_code == 200
    assert len(api.get("/api/v1/forecast?months=2").json()) == 2
    assert api.get("/api/v1/forecast?months=0").status_code == 422
    assert api.get("/api/v1/forecast?months=19").status_code == 422


def test_invalid_allocation_dimension_is_unprocessable() -> None:
    response = client().get("/api/v1/allocation?dimension=not-a-dimension")

    assert response.status_code == 422
    assert "Unsupported allocation dimension" in response.json()["detail"]


def test_full_analysis_contains_governance_views() -> None:
    response = client().post("/api/v1/analysis/run?months=2")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "summary",
        "recommendations",
        "anomalies",
        "forecast",
        "budgets",
        "allocation",
    }
    assert len(payload["forecast"]) == 2
    assert set(payload["allocation"]) == {
        "service",
        "enterprise_project",
        "environment",
        "cost_center",
        "product",
    }
