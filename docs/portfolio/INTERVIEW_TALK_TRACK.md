# Interview talk track

## 30-second summary

The project is a read-only Huawei Cloud FinOps decision platform. It combines
cost and capacity evidence to identify waste without creating reliability risk.
The core differentiators are explainable recommendations, conservative
non-overlapping savings, policy-as-code, and a complete deployment/observability
path.

## Two-minute walkthrough

1. Cost Center/Billing exports and AOM/CCE evidence are normalized into four
   canonical contracts.
2. The engine calculates allocation, budget status, robust anomalies, and a
   transparent monthly forecast.
3. Compute rules use P95 demand and headroom; Kubernetes request tuning happens
   before node-pool reduction.
4. Each recommendation includes evidence, risk, confidence, cost, saving, and a
   reversible action.
5. The API and control tower expose decisions, while OPA and approval rules
   prevent unsafe changes.
6. Kubernetes, Helm, Terraform, CI, CodeQL, and Trivy make the repository a
   deployable platform rather than a notebook.

## Likely questions

### Why median/MAD for anomalies?

Cloud cost data contains spikes and often violates normal-distribution
assumptions. Median/MAD remains stable when historical outliers exist.

### Why P95 instead of average utilization?

Average demand hides peak capacity needs. P95 captures sustained peak behavior
while remaining less sensitive than a single maximum.

### Why does the engine not execute changes?

Utilization does not contain full business criticality, release, DR, or
commitment context. Separating decision and execution limits blast radius and
creates an auditable approval boundary.

### How is double counting prevented?

Only the largest estimated saving per resource enters the executive portfolio.
Individual actions remain visible for scenario review.

### What would production version two add?

OBS/Billing/AOM collectors, recommendation persistence, SMN approval routing,
regional price catalog integration, realized-savings accounting, and canary
execution with automatic SLO rollback.
