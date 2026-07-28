# Optimization methodology

## Principles

The engine optimizes for the lowest **risk-adjusted** cost, not the lowest raw
cost. A recommendation must answer:

1. What evidence triggered the decision?
2. What action is proposed?
3. What could fail?
4. How confident is the evidence?
5. What savings are estimated?
6. Can the action be reversed?

## Observation statistics

For compute resources, the principal signals are:

- 95th percentile CPU utilization,
- 95th percentile memory utilization,
- 95th percentile network utilization,
- average requested CPU and memory for CCE,
- number of distinct observation days.

Linear interpolation is used for percentiles. P95 reduces sensitivity to one-off
noise while preserving peak demand better than a mean.

## Rule matrix

| Rule | Main evidence | Guardrail | Typical action |
|---|---|---|---|
| Compute rightsizing | P95 CPU < 35% and P95 memory < 45% | Retain policy headroom; canary test production | Evaluate one smaller flavor |
| Idle non-production | P95 CPU < 8%, memory < 15%, network < 10% | Non-production only; owner approval | Stop with recovery path |
| Capacity risk | P95 CPU >= 85% or memory >= 88% | No savings assigned | Scale or enable autoscaling |
| CCE request tuning | Requests materially exceed observed P95 | Tune requests before node reduction | Adjust pod requests |
| Non-prod schedule | Development/QA resource runs 24x7 | Automatic morning start and exception list | Business-hours schedule |
| Commitment candidate | Stable production pay-per-use baseline | Compare commitment coverage and lock-in | Review one-year option |
| Detached resource | EVS/EIP/ELB is detached, unbound, available, or idle | Snapshot or dependency check | Release resource |
| OBS lifecycle | Storage >= 500 GB | Validate access and retention policy | Tier or expire objects |
| Tag remediation | Required allocation identity missing | No savings claimed | Add mandatory cost tags |

Thresholds are policy defaults, not universal laws. They are intentionally
centralized, documented, and tested so an organization can calibrate them
against its SLOs and workload behavior.

## Savings calculation

For recommendation \(r\):

\[
\text{monthly saving}_r =
\max\left(0,\ \text{monthly cost} \times
\frac{\text{savings percentage}_r}{100}\right)
\]

Several rules can identify the same resource. Scheduling, rightsizing, stopping,
and commitment savings are not assumed to stack. The executive portfolio uses:

\[
\text{portfolio saving} =
\sum_{\text{resource } i}
\max_{r \in R_i}(\text{monthly saving}_r)
\]

This produces a deliberately conservative, non-overlapping estimate.

Annualized opportunity is monthly opportunity multiplied by 12. It is a
decision-support scenario, not guaranteed realized savings.

## Confidence

Recommendation confidence increases with distinct observation days:

\[
\text{confidence} =
\min\left(0.98,\ 0.55 +
\frac{\min(\text{days},30)}{30} \times 0.40\right)
\]

Inventory-only signals such as an unbound EIP use a high deterministic
confidence, while storage lifecycle recommendations use a lower confidence
until access patterns are validated.

## Cost anomaly detection

For each resource/day:

1. Aggregate amortized cost.
2. Use the preceding 14 observations, with at least seven required.
3. Calculate the rolling median \(m\).
4. Calculate median absolute deviation \(MAD\).
5. Scale dispersion by \(1.4826 \times MAD\).
6. Flag a positive spike when robust score >= 3.5 and deviation >= 25%.

\[
\text{score} = \frac{x - m}{\max(1.4826 \times MAD,\ 0.05m,\ 0.01)}
\]

Median/MAD is preferred over a simple z-score because cloud cost histories can
contain non-normal outliers.

## Forecast

Monthly amortized cost is aggregated and fitted with transparent least-squares
trend. Future months use the trend plus a widening 90% uncertainty band based
on residual standard deviation.

The model is intentionally explainable and dependency-light. A production
organization can replace the forecasting service with Prophet, ARIMA, or a
hierarchical model without changing the API or canonical data contract.

## Risk classes

| Risk | Meaning | Approval expectation |
|---|---|---|
| Low | Reversible or inventory-confirmed action | Resource owner |
| Medium | Performance or commitment impact possible | Owner + platform/finance |
| High | Active capacity/SLO risk | SRE/platform immediate review |
| Critical | Severe cost anomaly or governance breach | Incident process |

## Validation before execution

Every approved optimization should record:

- pre-change cost and utilization baseline,
- workload owner and maintenance window,
- rollback or recovery action,
- SLO and error-budget constraints,
- post-change P95 values,
- realized savings after a complete billing period.

## Exclusions

The demo does not:

- calculate authoritative regional Huawei Cloud prices,
- execute stop, resize, delete, or purchase actions,
- reconcile taxes, coupons, refunds, or negotiated discounts,
- assume a commitment recommendation is eligible,
- infer business criticality from utilization alone.
