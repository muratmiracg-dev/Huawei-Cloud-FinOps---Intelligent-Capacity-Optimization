# Project description - English

**Huawei Cloud FinOps & Intelligent Capacity Optimization Platform**

Designed and developed an explainable FinOps platform that transforms Huawei
Cloud cost, utilization, ownership, and capacity data into prioritized
engineering decisions. The solution covers cost allocation, budget governance,
robust anomaly detection, monthly forecasting, ECS/RDS/CCE rightsizing,
Kubernetes request efficiency, idle-resource detection, OBS lifecycle
opportunities, commitment candidates, and capacity-risk controls.

A deterministic six-month dataset makes the complete workflow reproducible. In
the demonstration portfolio, the engine evaluates $6,133.36 in monthly amortized
cost and identifies a conservative $1,520.70 monthly / $18,248.40 annualized
optimization opportunity while maintaining 97.43% allocation coverage and 100%
budget coverage. Savings are not double-counted; only the largest compatible
opportunity per resource contributes to the executive result.

The platform includes a Python analytics engine, FastAPI service, CLI, Docker
Compose control tower, Prometheus metrics, Grafana dashboard, hardened
Kubernetes manifests, Kustomize overlays, a production Helm chart, and
Terraform modules for Huawei Cloud CCE, OBS, and SMN. OPA policies enforce cost
labels, resource requests/limits, non-root execution, and capacity ceilings.
GitHub Actions adds Python 3.11/3.12 testing, a 90% coverage gate, deterministic
data drift checks, Terraform validation, container smoke testing, CodeQL, and
Trivy.

The public service is intentionally read-only: each recommendation contains
evidence, risk, confidence, savings, and a reversible action, while production
execution remains behind explicit owner approval.

**Technologies:** Huawei Cloud Cost Center, CCE, AOM, Cloud Eye, OBS, SMN, SWR,
Python, FastAPI, Docker, Kubernetes, Kustomize, Helm, Terraform, OPA/Rego,
Prometheus, Grafana, GitHub Actions, CodeQL, Trivy, Ruff, Pytest.
