# Validation evidence

Validation date: **2026-07-28**

## Local evidence

| Check | Result |
|---|---|
| Automated unit/integration/API/CLI tests | **53 / 53 passed** |
| Branch-aware package coverage | **97.09%** |
| Deterministic resource records | **15** |
| Deterministic daily cost records | **2,715** |
| Deterministic utilization samples | **1,320** |
| Analysis artifact generation | Passed |
| Executive policy gate | Passed with repository thresholds |
| JSON dashboard/report parsing | Passed |
| SVG render inspection | Passed |
| 18-slide PPTX render and overflow inspection | Passed |
| 20-page PDF render and page-by-page inspection | Passed |

## Reproducible commands

```bash
pytest --cov=finops --cov-report=term-missing --cov-report=xml
python scripts/generate_demo_data.py
PYTHONPATH=src python -m finops.cli \
  --data-dir data/demo \
  analyze \
  --forecast-months 3 \
  --output reports/demo-analysis.json
python scripts/finops_gate.py reports/demo-analysis.json \
  --max-monthly-cost 6500 \
  --min-allocation-coverage 95 \
  --max-high-risk 2
python scripts/verify_repository.py
python scripts/build_executive_pdf.py
```

## CI evidence expected on `main`

- Python 3.11 and 3.12 lint, test, and coverage
- deterministic demo drift check
- repository contract validation
- Terraform format/init/validate
- container build and readiness smoke test
- CodeQL Python analysis
- Trivy filesystem scan for high/critical findings

## Demo invariants

The validation script requires:

- monthly cost > 0,
- savings > 0 and lower than monthly cost,
- allocation coverage >= 90%,
- budget coverage >= 90%,
- at least one capacity-risk recommendation,
- at least one detected anomaly,
- forecast bounds containing predicted values,
- required repository and documentation files,
- parseable JSON assets,
- no obvious committed secret patterns.

## Limitations of local validation

Docker, Terraform, kubectl, Helm, OPA, and `gh` are not installed in the current
authoring environment. Their definitions are validated structurally here and
are configured for authoritative execution in GitHub Actions. Live Huawei Cloud
apply testing requires account-specific credentials, quotas, region availability,
and explicit user authorization; no live cloud resources were mutated.
