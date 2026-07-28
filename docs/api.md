# API reference

The API is read-only and generated from `finops.api.build_app`.

## Health

### `GET /health/live`

Returns `200` while the process can serve requests.

```json
{"status": "alive"}
```

### `GET /health/ready`

Loads the resource contract. Missing or malformed data returns `503`.

```json
{"status": "ready", "resources": 15}
```

## Executive summary

### `GET /api/v1/summary`

```json
{
  "current_monthly_cost": 6133.36,
  "estimated_monthly_savings": 1520.7,
  "savings_opportunity_pct": 24.79,
  "annualized_savings": 18248.4,
  "allocation_coverage_pct": 97.43,
  "budget_coverage_pct": 100.0,
  "recommendation_count": 21,
  "high_risk_count": 1,
  "anomaly_count": 2,
  "maturity_score": 96.4,
  "currency": "USD"
}
```

## Recommendations

### `GET /api/v1/recommendations?min_savings=100`

Returns recommendations at or above the requested monthly savings. Each item
contains type, action, rationale, current cost, savings, risk, confidence, and
evidence.

## Cost intelligence

- `GET /api/v1/anomalies`
- `GET /api/v1/forecast?months=3`
- `GET /api/v1/allocation?dimension=product`
- `GET /api/v1/budgets`

Supported allocation dimensions:

- service
- region
- enterprise_project
- environment
- owner
- cost_center
- product

An unsupported dimension returns `422` with valid choices.

## Full analysis

### `POST /api/v1/analysis/run?months=3`

Returns one response containing summary, recommendations, anomalies, forecast,
budgets, and the principal allocation views.

The endpoint executes analytics only. It does not resize, stop, delete,
purchase, or tag Huawei Cloud resources.

## Metrics

### `GET /metrics`

Prometheus gauges:

- `finops_current_monthly_cost`
- `finops_estimated_monthly_savings`
- `finops_savings_opportunity_ratio`
- `finops_allocation_coverage_ratio`
- `finops_budget_coverage_ratio`
- `finops_recommendations_total`
- `finops_high_risk_recommendations_total`
- `finops_cost_anomalies_total`
- `finops_maturity_score`

## OpenAPI

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
