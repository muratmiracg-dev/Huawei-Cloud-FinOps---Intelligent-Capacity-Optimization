# Executive summary

Rendered deliverables:

- [20-page bilingual executive PDF](../../output/pdf/Huawei_Cloud_FinOps_Executive_Report_EN_TR.pdf)
- [18-slide executive PowerPoint](../../presentation/Huawei_Cloud_FinOps_Executive_Deck_EN.pptx)

## Portfolio decision

The deterministic June 2026 portfolio carries **$6,133.36** in monthly
amortized cloud cost. The engine identifies a conservative **$1,520.70 monthly**
and **$18,248.40 annualized** optimization opportunity, equal to **24.79%** of
the current baseline.

Savings are deliberately non-overlapping: when multiple actions apply to one
resource, only the largest compatible opportunity is counted in the executive
total.

## Governance position

| Indicator | Result | Interpretation |
|---|---:|---|
| Allocation coverage | 97.43% | Above 95% target; one temporary host remains unallocated |
| Budget coverage | 100.00% | Every resource is in at least one budget scope |
| FinOps maturity | 96.4 / 100 | Strong visibility, governance, optimization, and automation evidence |
| Recommendations | 21 | Prioritized queue across capacity, waste, and commercial actions |
| Cost anomalies | 2 | Controlled synthetic spikes require owner investigation |
| High-risk decisions | 1 | Active CCE node capacity pressure |

## Budget position

| Budget | Actual utilization | Forecast utilization | Status |
|---|---:|---:|---|
| Non-Production | 133.24% | 135.58% | Breached |
| Cloud Portfolio Monthly | 105.75% | 107.60% | Breached |
| Commerce Product | 103.86% | 105.68% | Breached |
| Insights Product | 78.93% | 80.31% | Healthy |

The immediate portfolio priority is not a blanket cost reduction. It is a
sequenced plan:

1. protect the saturated CCE node before any node-pool reduction,
2. stop or schedule reversible non-production waste,
3. rightsize over-provisioned compute with canary validation,
4. release detached network/storage assets,
5. evaluate commitments only after the stable baseline is confirmed,
6. repair the remaining allocation gap.

## Top decision queue

| Resource | Decision | Monthly value | Risk |
|---|---|---:|---|
| `cce-commerce-prod-b` | Add capacity or enable autoscaling | Safety action | High |
| `cce-commerce-prod-a` | Evaluate 8-vCPU target with headroom | $207.20 | Medium |
| `developer-sandbox-01` | Stop after owner approval | $163.80 | Medium |
| `cce-dev-node-01` | Apply weekday schedule | $158.40 | Low |
| `analytics-postgres-prod` | Evaluate 4-vCPU target | $145.60 | Medium |
| `commerce-web-prod-02` | Evaluate 4-vCPU target | $142.80 | Medium |
| `orders-mysql-prod` | Compare one-year commitment | $124.20 | Medium |
| `commerce-web-prod-01` | Compare one-year commitment | $111.60 | Medium |

## Forecast

| Month | Predicted | 90% lower | 90% upper |
|---|---:|---:|---:|
| 2026-07 | $6,240.80 | $5,951.98 | $6,529.62 |
| 2026-08 | $6,346.65 | $5,938.19 | $6,755.10 |
| 2026-09 | $6,452.50 | $5,952.25 | $6,952.75 |

The upward trend increases budget pressure. Approved low-risk actions should be
completed first, while production rightsizing waits for capacity evidence and a
reversible maintenance plan.

## 30-day action plan

### Days 1–3

- respond to CCE capacity risk,
- investigate two cost anomalies,
- assign the unallocated temporary host,
- confirm export freshness and budget owners.

### Days 4–10

- stop the idle developer sandbox with recovery evidence,
- schedule approved development/QA compute,
- snapshot and release detached EVS/EIP/ELB assets,
- create OBS lifecycle simulation.

### Days 11–20

- canary the three largest rightsizing candidates,
- tune CCE requests before changing node-pool bounds,
- measure error rate, latency, saturation, and rollback time.

### Days 21–30

- compare commitments against the validated stable baseline,
- close or renew expiring exceptions,
- update budgets and forecasts,
- record approved and realized savings separately.

## Executive guardrails

- No automatic delete, stop, resize, or purchase.
- No production action without owner and SRE approval.
- No savings counted twice.
- No commitment recommendation treated as eligibility.
- No current-month expenditure treated as final reconciliation.
- No optimization closed without post-change SLO and billing evidence.
