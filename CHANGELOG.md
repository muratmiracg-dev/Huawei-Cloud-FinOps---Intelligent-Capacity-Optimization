# Changelog

All notable changes are documented in this file.

## [Unreleased]

### Fixed

- Budget status now uses each scope's own billing records. Actual and forecast
  cost were previously apportioned from the portfolio total by each scope's share
  of inventory `monthly_cost`, so a spike in one product or environment was spread
  across every budget and could hide the breach in the scope that caused it.
  Scope history is aligned to the portfolio calendar, so a month without spend
  counts as zero in the forecast. Demo budget utilization changes slightly
  (Commerce 103.86% -> 103.43%, Insights 78.93% -> 79.94%, Non-Production
  133.24% -> 133.66%); every status is unchanged.

## [1.0.0] - 2026-07-28

### Added

- Explainable FinOps analytics engine and FastAPI delivery layer
- Huawei Cloud billing export normalization
- Cost allocation, budgets, anomaly detection, and forecasting
- ECS, RDS, CCE, EVS, EIP, ELB, and OBS optimization rules
- Conservative non-overlapping savings calculation
- Deterministic six-month demo dataset and executive analysis
- Docker, Prometheus, Grafana, Kubernetes, Kustomize, Helm, and Terraform
- OPA guardrails, GitHub Actions, CodeQL, Trivy, and validation evidence
- English/Turkish documentation, executive report, and portfolio copy
